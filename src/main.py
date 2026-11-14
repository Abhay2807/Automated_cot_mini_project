"""Entry point for the Automated CoT mini project."""

import os
from pathlib import Path

from dotenv import load_dotenv

from src.llm_client import create_client, get_model_response
from src.planner import parse_model_response
from src.safe_tools import run_safe_tool


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "system_prompt.txt"


def load_system_prompt() -> str:
    """Read reusable system instructions from the prompts folder."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def run_task(user_task: str) -> None:
    """Run the bounded, iterative planning workflow."""
    load_dotenv(PROJECT_ROOT / ".env")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
    except ValueError:
        print("MAX_ITERATIONS must be a whole number.")
        return

    if max_iterations < 1:
        print("MAX_ITERATIONS must be at least 1.")
        return

    try:
        client = create_client()
    except (ValueError, Exception) as error:
        print(f"Client setup failed: {error}")
        return

    message_history = [
        {"role": "system", "content": load_system_prompt()},
        {"role": "user", "content": user_task},
    ]

    print("\nStarting the task...\n")

    for iteration in range(1, max_iterations + 1):
        print(f"--- Iteration {iteration}/{max_iterations} ---")

        try:
            raw_response = get_model_response(client, model, message_history)
            result = parse_model_response(raw_response)

            # Keep the assistant response in history for the next API request.
            message_history.append(
                {"role": "assistant", "content": raw_response}
            )

            step = result["step"]
            print(f"Step: {step}")
            print(result["content"])

            if step == "START":
                # Skip to the next loop iteration and make another API call.
                continue

            if step == "PLAN":
                action = result["action"]
                tool_input = result["tool_input"]

                try:
                    if action == "none":
                        print("No tool is needed. The model should provide OUTPUT.")
                        return
                    tool_result = run_safe_tool(action, tool_input)
                except ValueError as error:
                    print(f"Tool request rejected: {error}")
                    return

                print(f"Tool result: {tool_result}")

                # Give the result back to the model as conversation context.
                message_history.append({
                    "role": "user",
                    "content": (
                        "The approved local tool has completed. "
                        f"Action: {action}. Result: {tool_result}. "
                        "Continue the task and return the next JSON step."
                    ),
                })
                print(f"Updated conversation history: {len(message_history)} messages")
                continue

            if step == "OUTPUT":
                print("\nFinal answer:")
                print(result["content"])
                return

        except Exception as error:
            # Covers API/network errors, parsing errors and unexpected failures.
            print(f"An error occurred: {error}")
            return

    print(
        "\nStopped: maximum iteration limit reached. "
        "The model did not provide an OUTPUT step in time."
    )


def main() -> None:
    print("=== Automated CoT Mini Project ===")
    user_task = input("Enter a task: ").strip()

    if not user_task:
        print("Please enter a task.")
        return

    run_task(user_task)


if __name__ == "__main__":
    main()
