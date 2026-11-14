"""Parsing and validating the model's structured response."""

import json


def parse_model_response(raw_response: str) -> dict:
    """Convert JSON text to a Python dictionary and validate its shape."""
    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise ValueError(f"Model returned invalid JSON: {error}") from error

    if not isinstance(result, dict):
        raise ValueError("The response must be a JSON object.")

    step = result.get("step")
    if step not in {"START", "PLAN", "OUTPUT"}:
        raise ValueError(f"Unexpected step value: {step}")
    
    content = result.get("content")

    if not isinstance(content, str):
        raise ValueError(
            f"'content' must be a string. "
            f"Received type: {type(content).__name__}, value: {content!r}"
        )

    if step == "PLAN":
        if result.get("action") not in {"count_words", "uppercase_text", "character_count", "none"}:
            raise ValueError("PLAN contains an unsupported action.")

        if not isinstance(result.get("tool_input"), str):
            raise ValueError("PLAN must contain a string 'tool_input'.")

    return result
