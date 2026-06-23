#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


STAGES = ["plan", "design", "build", "test", "review", "documentation", "release"]


class ValidationError(Exception):
    pass


def usage_error(message):
    print(message, file=sys.stderr)
    sys.exit(2)


def strip_comment(line):
    in_single = False
    in_double = False
    for index, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:index].rstrip()
    return line.rstrip()


def load_yaml_subset(path):
    raw_lines = Path(path).read_text(encoding="utf-8").splitlines()
    lines = []

    for line_no, raw in enumerate(raw_lines, start=1):
        if "\t" in raw:
            raise ValidationError(f"{path}:{line_no}: tabs are not allowed in metadata.yaml")

        stripped_comment = strip_comment(raw)
        if not stripped_comment.strip():
            continue

        indent = len(stripped_comment) - len(stripped_comment.lstrip(" "))
        lines.append((indent, stripped_comment[indent:], line_no))

    index = 0

    def parse_scalar(value, line_no):
        value = value.strip()

        if value == "[]":
          return []

        if value == "{}":
          return {}

        if value in ("true", "false"):
          return value == "true"

        if value in ("null", "~"):
          return None

        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValidationError(f"{path}:{line_no}: invalid quoted string: {exc}") from exc

        if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            return value[1:-1]

        return value

    def split_key_value(text, line_no):
        if ":" not in text:
            raise ValidationError(f"{path}:{line_no}: expected key/value pair")

        key, value = text.split(":", 1)
        key = key.strip()
        if not key:
            raise ValidationError(f"{path}:{line_no}: empty key")

        return key, value.strip()

    def looks_like_inline_mapping(text):
        if ":" not in text:
            return False
        key = text.split(":", 1)[0].strip()
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_-]*$", key))

    def parse_block(expected_indent):
        nonlocal index
        if index >= len(lines):
            return {}

        indent, text, line_no = lines[index]
        if indent < expected_indent:
            return {}
        if indent > expected_indent:
            raise ValidationError(
                f"{path}:{line_no}: unexpected indentation {indent}, expected {expected_indent}"
            )

        if text.startswith("- "):
            return parse_list(expected_indent)
        return parse_map(expected_indent)

    def parse_map(expected_indent):
        nonlocal index
        result = {}

        while index < len(lines):
            indent, text, line_no = lines[index]
            if indent < expected_indent:
                break
            if indent > expected_indent:
                raise ValidationError(
                    f"{path}:{line_no}: unexpected indentation {indent}, expected {expected_indent}"
                )
            if text.startswith("- "):
                break

            key, value = split_key_value(text, line_no)
            index += 1

            if value == "":
                if index < len(lines) and lines[index][0] > expected_indent:
                    result[key] = parse_block(lines[index][0])
                else:
                    result[key] = ""
            else:
                result[key] = parse_scalar(value, line_no)

        return result

    def parse_list(expected_indent):
        nonlocal index
        result = []

        while index < len(lines):
            indent, text, line_no = lines[index]
            if indent < expected_indent:
                break
            if indent != expected_indent or not text.startswith("- "):
                break

            value = text[2:].strip()
            index += 1

            if value == "":
                if index < len(lines) and lines[index][0] > expected_indent:
                    result.append(parse_block(lines[index][0]))
                else:
                    result.append("")
            elif looks_like_inline_mapping(value):
                key, scalar = split_key_value(value, line_no)
                item = {key: parse_scalar(scalar, line_no) if scalar else {}}
                if index < len(lines) and lines[index][0] > expected_indent:
                    nested = parse_block(lines[index][0])
                    if isinstance(nested, dict):
                        item.update(nested)
                    else:
                        item[key] = nested
                result.append(item)
            else:
                result.append(parse_scalar(value, line_no))

        return result

    parsed = parse_block(0)
    if index != len(lines):
        _, _, line_no = lines[index]
        raise ValidationError(f"{path}:{line_no}: could not parse metadata.yaml")
    return parsed


def resolve_ref(schema, ref):
    if not ref.startswith("#/"):
        raise ValidationError(f"unsupported schema ref: {ref}")

    node = schema
    for part in ref[2:].split("/"):
        node = node[part]
    return node


def check_type(value, expected):
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate_schema(value, schema_node, root_schema, path="$"):
    errors = []

    if "$ref" in schema_node:
        return validate_schema(value, resolve_ref(root_schema, schema_node["$ref"]), root_schema, path)

    expected_type = schema_node.get("type")
    if expected_type and not check_type(value, expected_type):
        errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
        return errors

    if "enum" in schema_node and value not in schema_node["enum"]:
        allowed = ", ".join(str(item) for item in schema_node["enum"])
        errors.append(f"{path}: expected one of [{allowed}], got {value!r}")

    if "pattern" in schema_node and isinstance(value, str):
        if not re.match(schema_node["pattern"], value):
            errors.append(f"{path}: value {value!r} does not match {schema_node['pattern']}")

    if "minLength" in schema_node and isinstance(value, str):
        if len(value) < schema_node["minLength"]:
            errors.append(f"{path}: string is shorter than {schema_node['minLength']}")

    if "minItems" in schema_node and isinstance(value, list):
        if len(value) < schema_node["minItems"]:
            errors.append(f"{path}: array has fewer than {schema_node['minItems']} items")

    if isinstance(value, dict):
        required = schema_node.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema_node.get("properties", {})
        if schema_node.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")

        for key, child_schema in properties.items():
            if key in value:
                errors.extend(validate_schema(value[key], child_schema, root_schema, f"{path}.{key}"))

    if isinstance(value, list) and "items" in schema_node:
        for index, item in enumerate(value):
            errors.extend(validate_schema(item, schema_node["items"], root_schema, f"{path}[{index}]"))

    return errors


def validate_stage_outputs(metadata):
    if not isinstance(metadata, dict):
        return []

    errors = []
    stage_outputs = metadata.get("stage_outputs", {})

    if not isinstance(stage_outputs, dict):
        return ["$.stage_outputs: expected object"]

    for stage in STAGES:
        output = stage_outputs.get(stage)
        if not isinstance(output, dict):
            continue

        expected_result = f"{stage}/result.md"
        expected_handoff = f"{stage}/handoff.md"

        if output.get("result") != expected_result:
            errors.append(f"$.stage_outputs.{stage}.result: expected {expected_result}")
        if output.get("handoff") != expected_handoff:
            errors.append(f"$.stage_outputs.{stage}.handoff: expected {expected_handoff}")

        if stage == "build" and output.get("tasks") != "build/tasks.md":
            errors.append("$.stage_outputs.build.tasks: expected build/tasks.md")

    return errors


def validate_stage_statuses(metadata):
    if not isinstance(metadata, dict):
        return []

    errors = []
    stage_statuses = metadata.get("stage_statuses", {})

    if not isinstance(stage_statuses, dict):
        return ["$.stage_statuses: expected object"]

    current_stage = metadata.get("current_stage")
    current_status = metadata.get("current_status")

    if current_stage in STAGES:
        stage_status = stage_statuses.get(current_stage)
        if stage_status != current_status:
            errors.append(
                "$.stage_statuses."
                f"{current_stage}: expected {current_status!r} to match $.current_status"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate SDLC case metadata.yaml against schema.")
    parser.add_argument("metadata")
    parser.add_argument("schema")
    parser.add_argument("--case-id")
    parser.add_argument("--stage")
    args = parser.parse_args()

    try:
        metadata = load_yaml_subset(args.metadata)
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
        errors = validate_schema(metadata, schema, schema)
        errors.extend(validate_stage_outputs(metadata))
        errors.extend(validate_stage_statuses(metadata))

        if isinstance(metadata, dict):
            if args.case_id and metadata.get("case_id") != args.case_id:
                errors.append(
                    f"$.case_id: expected {args.case_id}, got {metadata.get('case_id', 'missing')}"
                )

            if args.stage and metadata.get("current_stage") != args.stage:
                errors.append(
                    "$.current_stage: "
                    f"expected {args.stage}, got {metadata.get('current_stage', 'missing')}"
                )

        if errors:
            for error in errors:
                print(f"{args.metadata}: {error}", file=sys.stderr)
            return 1

        return 0
    except (OSError, ValidationError, json.JSONDecodeError) as exc:
        print(f"{args.metadata}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
