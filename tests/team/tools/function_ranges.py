import ast

targets = {
    "backend/routes/patient.py": ["get_available_slots", "get_appointments", "book_appointment", "cancel_appointment"],
    "backend/routes/doctor.py": ["update_appointment_status"],
    "backend/routes/admin.py": ["update_appointment", "toggle_patient_blacklist"],
}

for path, names in targets.items():
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            print(f"{path}  {node.name}  lines {start}-{node.end_lineno}")
