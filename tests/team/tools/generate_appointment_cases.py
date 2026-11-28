"""Read and validate OpenAPI and generate deterministic per-field EP/BVA cases."""

import argparse
import copy
import json
import re
from datetime import date, timedelta
from pathlib import Path

import yaml
from openapi_spec_validator import validate


TEST_DATE = date(2030, 1, 15)
ROLES = ("anonymous", "patient", "doctor", "admin")
WRONG_TYPES = {"integer": "abc", "string": 42}


def dereference(spec, node):
    if isinstance(node, list):
        return [dereference(spec, element) for element in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        value = spec
        for part in node["$ref"].removeprefix("#/").split("/"):
            value = value[part]
        return dereference(spec, value)
    return {key: dereference(spec, value) for key, value in node.items()}


def boundary_values(schema):
    values = list(schema.get("x-boundary-values", []))
    values += [(TEST_DATE + timedelta(days=delta)).isoformat() for delta in schema.get("x-days", [])]
    values += [f"{hour:02}:00" for limit in schema.get("x-hour-boundaries", [])
               for hour in (limit - 1, limit, limit + 1)]
    for limit in schema.get("x-minute-boundaries", []):
        hour, minute = map(int, limit.split(":"))
        for delta in (-1, 0, 1):
            h, m = divmod(hour * 60 + minute + delta, 60)
            values.append(f"{h:02}:{m:02}")
    if schema["type"] == "integer":
        for field in ("minimum", "maximum"):
            if field in schema:
                values += [schema[field] + delta for delta in (-1, 0, 1)]
    return values


def accepted(schema, value):
    if value is None:
        return schema.get("nullable", False)
    if schema["type"] == "integer":
        return type(value) is int and schema.get("minimum", value) <= value <= schema.get("maximum", value)
    if not isinstance(value, str):
        return False
    if schema.get("format") == "date":
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
    if "enum" in schema and value not in schema["enum"]:
        return False
    if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
        return False
    periods = schema.get("x-open-ranges")
    return not periods or any(first <= int(value[:2]) < last for first, last in periods)


def generate(spec):
    cases = []
    for path, methods in spec["paths"].items():
        for method, raw in methods.items():
            op = dereference(spec, raw)
            operation = op["operationId"]
            setup = op["x-test"]
            default = {"query": {}, "path": {}, "body": {}}
            fields = []
            for p in op.get("parameters", []):
                fields.append((p["in"], p["name"], p["schema"], p.get("required", False), p))
            if "requestBody" in op:
                body = op["requestBody"]["content"]["application/json"]["schema"]
                for name, rules in body["properties"].items():
                    fields.append(("body", name, rules, name in body.get("required", []), rules))
            for location, name, rules, _, _ in fields:
                default[location][name] = rules["example"]

            def add(suffix, expected=200, *, actor=None, inputs=None, raw_body=None,
                    field=None, probe="valid", fixture=None, clock=None):
                response = op["responses"].get(str(expected))
                if response is None:
                    raise ValueError(f"{operation} has no declared response for {expected}")
                body_schema = response.get("content", {}).get("application/json", {}).get("schema")
                cases.append({
                    "id": f"GEN-{operation}-{suffix}", "operation": operation, "method": method.upper(),
                    "path": path, "actor": actor or setup["actor"], "fixture": fixture or setup.get("fixture"),
                    "input": copy.deepcopy(inputs if inputs is not None else default),
                    "raw_body": raw_body, "expected_status": expected, "response_schema": body_schema,
                    "field": field, "probe": probe,
                })
                if clock is not None:
                    cases[-1]["clock"] = clock

            add("valid")
            for actor in ROLES:
                if actor == setup["actor"]:
                    continue
                code = 200 if actor in setup["roles"] else (401 if actor == "anonymous" else 403)
                add("role-" + actor, code, actor=actor, probe="role")
            for location, name, rules, required, metadata in fields:
                identifier = f"{location}-{name}"
                if location != "path":
                    inputs = copy.deepcopy(default)
                    del inputs[location][name]
                    add(identifier + "-missing", 400 if required else 200, inputs=inputs,
                        field=identifier, probe="missing")
                boundaries = boundary_values(rules)
                boundary_keys = set(map(json.dumps, boundaries))
                values = [*rules.get("enum", []), *rules.get("x-values", []), *boundaries]
                if location == "body":
                    values += [None, WRONG_TYPES[rules["type"]]]
                for encoded in dict.fromkeys(map(json.dumps, values)):
                    value = json.loads(encoded)
                    if type(value) is type(rules["example"]) and value == rules["example"]:
                        continue
                    inputs = copy.deepcopy(default)
                    inputs[location][name] = value
                    invalid = metadata.get("x-invalid", 400)
                    default_code = 200 if accepted(rules, value) else invalid
                    code = metadata.get("x-status", {}).get(str(value), default_code)
                    label = re.sub(r"[^A-Za-z0-9]+", "-", str(value)).strip("-") or "empty"
                    if str(value).startswith("-"):
                        label = "negative-" + label
                    add(identifier + "-" + label, code, inputs=inputs, field=identifier,
                        probe="boundary" if encoded in boundary_keys else "partition")
                for probe in rules.get("x-partitions", []):
                    inputs = copy.deepcopy(default)
                    inputs[location][name] = probe["value"]
                    add(identifier + "-" + probe["id"], probe["status"], inputs=inputs,
                        field=identifier, fixture=probe.get("fixture"), probe="partition")
            for probe in op.get("x-cases", []):
                inputs = copy.deepcopy(default)
                for location, values in probe.get("input", {}).items():
                    inputs[location].update(values)
                status = probe["status"]
                for location, name, rules, _, _ in fields:
                    if probe.get("require_conforming") == f"{location}-{name}" and not accepted(rules, inputs[location][name]):
                        status = 400
                add(probe["id"], status, inputs=inputs, probe=probe["probe"],
                    fixture=probe.get("fixture"), clock=probe.get("clock"))
            if "requestBody" in op:
                for label, value in (("null", "null"), ("array", "[]"), ("malformed", "{")):
                    add("json-" + label, 400, raw_body=value, probe="invalid-document")
                inputs = copy.deepcopy(default)
                inputs["body"]["synthetic_extra"] = "unused"
                add("extra-field", inputs=inputs, probe="unknown-key")
    identifiers = {c["id"] for c in cases}
    if len(identifiers) != len(cases):
        raise ValueError("Generated cases need distinct identifiers")
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()
    spec = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    if args.overlay:
        overlay = yaml.safe_load(args.overlay.read_text(encoding="utf-8"))
        spec["info"]["version"] = overlay["version"]
        for change in overlay["changes"]:
            target = spec
            for key in change["path"][:-1]:
                target = target[key]
            target[change["path"][-1]] = change["value"]
    validate(spec)
    result = {"version": spec["info"]["version"], "clock_date": str(TEST_DATE), "cases": generate(spec)}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['version']}: {len(result['cases'])} generated cases.")


if __name__ == "__main__":
    main()
