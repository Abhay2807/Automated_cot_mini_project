
import unittest

from src.safe_tools import (
    count_words,
    uppercase_text,
    character_count,
    run_safe_tool,
)


class TestSafeTools(unittest.TestCase):

    def test_count_words(self):
        result = count_words("Python is useful")
        self.assertEqual(result, "3")

    def test_count_words_multiple_spaces(self):
        result = count_words("Python   is   useful")
        self.assertEqual(result, "3")

    def test_count_words_empty_string(self):
        result = count_words("")
        self.assertEqual(result, "0")

    def test_uppercase_text(self):
        result = uppercase_text("hello python")
        self.assertEqual(result, "HELLO PYTHON")

    def test_character_count(self):
        result = character_count("Hello World")
        self.assertEqual(result, "11")

    def test_invalid_input_type(self):
        with self.assertRaises(ValueError):
            count_words(123)

    def test_input_length_limit(self):
        long_text = "A" * 5001

        with self.assertRaises(ValueError):
            count_words(long_text)

    def test_unknown_action(self):
        with self.assertRaises(ValueError):
            run_safe_tool("delete_database", "test")

    def test_none_action(self):
        result = run_safe_tool("none", "")
        self.assertEqual(result, "No tool was executed.")


if __name__ == "__main__":
    unittest.main()
