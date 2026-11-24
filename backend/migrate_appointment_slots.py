"""Upgrade an offline copy of an existing MediHub SQLite database in place."""

import argparse
import re
import sqlite3
from contextlib import closing
from pathlib import Path


LEGACY_CONSTRAINT = re.compile(
    r",\s*CONSTRAINT unique_doctor_slot UNIQUE\s*"
    r"\(doctor_id,\s*appointment_date,\s*appointment_time\)", re.IGNORECASE,
)
INDEXES = {
    'unique_booked_doctor_slot': ('doctor_id', 'appointment_date', 'appointment_time'),
    'unique_booked_patient_time': ('patient_id', 'appointment_date', 'appointment_time'),
}


def upgrade(connection):
    # Rebuild without re-pointing child foreign keys to a temporary table name.
    connection.execute('PRAGMA foreign_keys = OFF')
    with connection:
        connection.execute('BEGIN IMMEDIATE')
        schema = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE type = 'table' AND name = 'appointments'"
        ).fetchone()
        if schema is None:
            raise ValueError('This database has no appointments table')
        original = schema[0]
        ddl, removed = LEGACY_CONSTRAINT.subn('', original)
        if removed == 0:
            indexes = {row[1] for row in connection.execute('PRAGMA index_list(appointments)')}
            if INDEXES.keys() <= indexes:
                return False
            raise ValueError('Unsupported appointments schema')
        replacement, replacements = re.subn(
            r'^CREATE TABLE (?:appointments|"appointments")\s*\(',
            'CREATE TABLE appointments_rebuilt (', ddl, count=1, flags=re.IGNORECASE,
        )
        if removed != 1 or replacements != 1:
            raise ValueError('Unsupported appointments schema')
        dependencies = connection.execute(
            "SELECT sql FROM sqlite_schema WHERE tbl_name = 'appointments' "
            "AND type IN ('index', 'trigger') AND sql IS NOT NULL"
        ).fetchall()
        connection.execute(replacement)
        connection.execute('INSERT INTO appointments_rebuilt SELECT * FROM appointments')
        connection.execute('DROP TABLE appointments')
        connection.execute('ALTER TABLE appointments_rebuilt RENAME TO appointments')
        for (statement,) in dependencies:
            connection.execute(statement)
        for index, columns in INDEXES.items():
            connection.execute(
                f"CREATE UNIQUE INDEX {index} ON appointments ({', '.join(columns)}) WHERE status = 'booked'"
            )
        if connection.execute('PRAGMA foreign_key_check').fetchone() is not None:
            raise ValueError('Foreign key validation failed; the migration was rolled back')
        return True


def migrate(path):
    uri = Path(path).resolve(strict=True).as_uri() + '?mode=rw'
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        return upgrade(connection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path, help='Path to an offline, backed-up SQLite file')
    args = parser.parse_args()
    print('Migrated appointment slots' if migrate(args.database) else 'Appointment slot indexes already installed')


if __name__ == '__main__':
    main()
