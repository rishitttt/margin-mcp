"""Bounded schema diagnostics without echoing caller values or unknown field names."""

from itertools import islice

from jsonschema import Draft202012Validator, FormatChecker


def validation_summary(schema, value):
    """Return schema-owned guidance, or None when input matches the schema."""
    names = set()

    def collect(node):
        if isinstance(node, dict):
            names.update(node.get("properties", {}))
            for child in node.values():
                collect(child)
        elif isinstance(node, list):
            for child in node:
                collect(child)

    collect(schema)
    messages = []
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in islice(validator.iter_errors(value), 16):
        parts = [
            str(part)
            if (isinstance(part, int) and 0 <= part <= 200)
            or (isinstance(part, str) and part in names)
            else "[entry]"
            for part in list(error.absolute_path)[:8]
        ]
        path = "/" + "/".join(part.replace("~", "~0").replace("/", "~1") for part in parts)
        if error.validator == "additionalProperties":
            allowed = list(error.schema.get("properties", {}))[:24]
            reason = "unexpected fields; allowed fields: " + (", ".join(allowed) or "none")
        elif error.validator == "required":
            missing = [name for name in error.validator_value if name not in error.instance][:24]
            reason = "missing required fields: " + ", ".join(missing)
        elif error.validator == "type":
            expected = error.validator_value
            reason = "expected type: " + (
                ", ".join(expected) if isinstance(expected, list) else expected
            )
        elif error.validator == "format":
            reason = "expected format: " + error.validator_value
        elif error.validator == "enum":
            reason = "must match an allowed enum value in the catalog schema"
        else:
            reason = "does not satisfy the catalog schema constraint"
        message = f"{path}: {reason}."
        if message not in messages:
            messages.append(message)
        if len(messages) == 4:
            break
    return " ".join(messages)[:1800] if messages else None
