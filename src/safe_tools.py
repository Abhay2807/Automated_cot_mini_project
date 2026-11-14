"""Small, predefined local functions that the model may request."""

MAX_TEXT_LENGTH = 5000


def _validate_text(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Tool input must be a string.")

    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"Tool input is too long. Maximum is {MAX_TEXT_LENGTH} characters.")

    return value


def count_words(text: str) -> str:
    """Return the number of whitespace-separated words."""
    text = _validate_text(text)
    return str(len(text.split()))


def uppercase_text(text: str) -> str:
    """Return the text converted to uppercase."""
    text = _validate_text(text)
    return text.upper()

def character_count(text: str) -> str:
    """Count all characters including space"""
    text = _validate_text(text)
    return str(len(text))

# Allowlist: only actions registered here can be executed.
SAFE_TOOLS = {
    "count_words": count_words,
    "uppercase_text": uppercase_text,
    "character_count" : character_count
}


def run_safe_tool(action: str, tool_input: str) -> str:
    """Execute one registered function; reject every other action."""
    if action == "none":
        return "No tool was executed."

    tool_function = SAFE_TOOLS.get(action)
    if tool_function is None:
        raise ValueError(f"Action is not allowed: {action}")

    return tool_function(tool_input)
