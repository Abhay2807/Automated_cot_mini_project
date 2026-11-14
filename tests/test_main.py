
"""Tests for the Automated CoT workflow in main.py."""

import json
import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.main import run_task


class TestRunTask(unittest.TestCase):

    def test_direct_output(self):
        """The workflow should finish when the model returns OUTPUT."""

        output_response = json.dumps({
            "step": "OUTPUT",
            "content": "The answer is 42."
        })

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value=output_response),
            patch("src.main.run_safe_tool") as mock_tool,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("What is the answer?")

        self.assertIn("The answer is 42.", captured_output.getvalue())
        mock_tool.assert_not_called()

    def test_start_plan_output_flow(self):
        """The workflow should execute a tool and pass its result back to the model."""

        responses = [
            json.dumps({
                "step": "START",
                "content": "I will analyse the text."
            }),
            json.dumps({
                "step": "PLAN",
                "content": "I will count the words.",
                "action": "count_words",
                "tool_input": "Python is useful"
            }),
            json.dumps({
                "step": "OUTPUT",
                "content": "The text contains 3 words."
            }),
        ]

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", side_effect=responses) as mock_api,
            patch("src.main.run_safe_tool", return_value="3") as mock_tool,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Count the words in this text.")

        output = captured_output.getvalue()

        self.assertIn("Tool result: 3", output)
        self.assertIn("The text contains 3 words.", output)

        mock_tool.assert_called_once_with(
            "count_words",
            "Python is useful"
        )

        self.assertEqual(mock_api.call_count, 3)

        # Check that the tool result was sent back in the next API request.
        second_api_history = mock_api.call_args_list[2].args[2]

        self.assertIn(
            "Result: 3.",
            second_api_history[-2]["content"]
        )

    def test_api_exception(self):
        """The workflow should stop if the API call fails."""

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch(
                "src.main.get_model_response",
                side_effect=RuntimeError("API connection failed")
            ),
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn(
            "An error occurred: API connection failed",
            captured_output.getvalue()
        )

    def test_invalid_json_response(self):
        """The workflow should stop if the model returns invalid JSON."""

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value="This is not JSON"),
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn("Model returned invalid JSON", captured_output.getvalue())

    def test_max_iteration_limit(self):
        """The workflow should stop after the configured number of iterations."""

        start_response = json.dumps({
            "step": "START",
            "content": "I am still analysing."
        })

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "2"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value=start_response) as mock_api,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertEqual(mock_api.call_count, 2)

        self.assertIn(
            "maximum iteration limit reached",
            captured_output.getvalue()
        )

    def test_invalid_max_iterations(self):
        """The workflow should reject a non-numeric iteration limit."""

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "abc"}),
            patch("src.main.load_dotenv"),
            patch("src.main.create_client") as mock_client,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn(
            "MAX_ITERATIONS must be a whole number.",
            captured_output.getvalue()
        )

        mock_client.assert_not_called()

    def test_zero_max_iterations(self):
        """The workflow should reject zero iterations."""

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "0"}),
            patch("src.main.load_dotenv"),
            patch("src.main.create_client") as mock_client,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn(
            "MAX_ITERATIONS must be at least 1.",
            captured_output.getvalue()
        )

        mock_client.assert_not_called()

    def test_none_action_does_not_execute_tool(self):
        """The workflow should stop without executing a tool for action='none'."""

        plan_response = json.dumps({
            "step": "PLAN",
            "content": "No local tool is required.",
            "action": "none",
            "tool_input": ""
        })

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test system prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value=plan_response),
            patch("src.main.run_safe_tool") as mock_tool,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Explain Python.")

        self.assertIn("No tool is needed.", captured_output.getvalue())
        mock_tool.assert_not_called()

    def test_unsupported_action_is_rejected(self):
        invalid_response = json.dumps({
            "step": "PLAN",
            "content": "Trying an unsupported action.",
            "action": "execute_python",
            "tool_input": "print('hello')"
        })

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value=invalid_response),
            patch("src.main.run_safe_tool") as mock_tool,
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn("unsupported action", captured_output.getvalue())
        mock_tool.assert_not_called()

    def test_tool_execution_error(self):
        plan_response = json.dumps({
            "step": "PLAN",
            "content": "Count the words.",
            "action": "count_words",
            "tool_input": "Hello world"
        })

        with (
            patch.dict(os.environ, {"MAX_ITERATIONS": "5"}),
            patch("src.main.load_dotenv"),
            patch("src.main.load_system_prompt", return_value="Test prompt"),
            patch("src.main.create_client"),
            patch("src.main.get_model_response", return_value=plan_response),
            patch(
                "src.main.run_safe_tool",
                side_effect=ValueError("Tool input is too long.")
            ),
        ):
            captured_output = StringIO()

            with redirect_stdout(captured_output):
                run_task("Test task")

        self.assertIn(
            "Tool request rejected: Tool input is too long.",
            captured_output.getvalue()
        )


if __name__ == "__main__":
    unittest.main()
