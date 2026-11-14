"""OpenAI client setup and API request."""

import os
from openai import OpenAI


def create_client() -> OpenAI:
    """Create the SDK client using OPENAI_API_KEY from the environment."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY was not found. Add it to your .env file."
        )

    return OpenAI(api_key=api_key)


def get_model_response(client: OpenAI, model: str, messages: list) -> str:
    """Send the current message history and return the assistant's text."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("The model returned an empty response.")

    return content
