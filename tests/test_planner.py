
import unittest

from src.planner import parse_model_response


class TestPlanner(unittest.TestCase):

    # -------------------------
    # Valid response tests
    # -------------------------

    def test_valid_start_response(self):
        raw_response = '''
        {
            "step": "START",
            "content": "I will help with your task."
        }
        '''

        result = parse_model_response(raw_response)

        self.assertEqual(result["step"], "START")
        self.assertEqual(result["content"], "I will help with your task.")

    def test_valid_plan_response(self):
        raw_response = '''
        {
            "step": "PLAN",
            "content": "I will count the words.",
            "action": "count_words",
            "tool_input": "Hello World"
        }
        '''

        result = parse_model_response(raw_response)

        self.assertEqual(result["step"], "PLAN")
        self.assertEqual(result["action"], "count_words")
        self.assertEqual(result["tool_input"], "Hello World")

    def test_valid_output_response(self):
        raw_response = '''
        {
            "step": "OUTPUT",
            "content": "There are 2 words."
        }
        '''

        result = parse_model_response(raw_response)

        self.assertEqual(result["step"], "OUTPUT")
        self.assertEqual(result["content"], "There are 2 words.")

    # -------------------------
    # Invalid JSON tests
    # -------------------------

    def test_invalid_json(self):
        raw_response = '{"step": "START", "content": }'

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            parse_model_response(raw_response)

    def test_json_array_instead_of_object(self):
        raw_response = '["START", "Hello"]'

        with self.assertRaisesRegex(ValueError, "JSON object"):
            parse_model_response(raw_response)

    # -------------------------
    # Response structure tests
    # -------------------------

    def test_missing_step(self):
        raw_response = '{"content": "Hello"}'

        with self.assertRaisesRegex(ValueError, "Unexpected step"):
            parse_model_response(raw_response)

    def test_invalid_step(self):
        raw_response = '''
        {
            "step": "UNKNOWN",
            "content": "Hello"
        }
        '''

        with self.assertRaisesRegex(ValueError, "Unexpected step"):
            parse_model_response(raw_response)

    def test_missing_content(self):
        raw_response = '{"step": "START"}'

        with self.assertRaisesRegex(ValueError, "content"):
            parse_model_response(raw_response)

    def test_content_is_not_string(self):
        raw_response = '''
        {
            "step": "START",
            "content": 123
        }
        '''

        with self.assertRaisesRegex(ValueError, "content"):
            parse_model_response(raw_response)

    # -------------------------
    # PLAN validation tests
    # -------------------------

    def test_unsupported_action(self):
        raw_response = '''
        {
            "step": "PLAN",
            "content": "Delete something.",
            "action": "delete_database",
            "tool_input": "test"
        }
        '''

        with self.assertRaisesRegex(ValueError, "unsupported action"):
            parse_model_response(raw_response)

    def test_missing_tool_input(self):
        raw_response = '''
        {
            "step": "PLAN",
            "content": "Count the words.",
            "action": "count_words"
        }
        '''

        with self.assertRaisesRegex(ValueError, "tool_input"):
            parse_model_response(raw_response)

    def test_tool_input_is_not_string(self):
        raw_response = '''
        {
            "step": "PLAN",
            "content": "Count the words.",
            "action": "count_words",
            "tool_input": 123
        }
        '''

        with self.assertRaisesRegex(ValueError, "tool_input"):
            parse_model_response(raw_response)


if __name__ == "__main__":
    unittest.main()
