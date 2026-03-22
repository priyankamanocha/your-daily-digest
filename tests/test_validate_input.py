"""Tests for validate_input.py."""
import os
import sys
import unittest
from unittest.mock import patch
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from validate_input import validate


class TestValidateInput(unittest.TestCase):
    def test_valid_minimal_payload(self):
        result = validate({"topic": "claude-code"})
        self.assertTrue(result["valid"])
        self.assertEqual(result["topic"], "claude-code")
        self.assertEqual(result["hints"], [])
        self.assertEqual(result["snippets"], [])
        self.assertEqual(result["since"], "1")
        self.assertEqual(result["since_window"], {})
        self.assertFalse(result["no_diff"])

    def test_valid_payload_with_optional_fields(self):
        result = validate(
            {
                "topic": "ai agents",
                "hints": ["@karpathy", "3blue1brown"],
                "snippets": ["one", "two"],
                "since": "7d",
                "since_window": {
                    "start_date": "2026-03-01",
                    "end_date": "2026-03-07",
                    "label": "last week",
                },
                "no_diff": True,
            }
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["topic"], "ai agents")
        self.assertEqual(result["hints"], ["@karpathy", "3blue1brown"])
        self.assertEqual(result["snippets"], ["one", "two"])
        self.assertEqual(result["since"], "7d")
        self.assertTrue(result["no_diff"])

    def test_topic_is_required(self):
        self.assertFalse(validate({})["valid"])
        self.assertEqual(validate({})["error"], "topic is required")

    def test_topic_cannot_be_whitespace(self):
        result = validate({"topic": "   "})
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "topic cannot be empty")

    def test_topic_is_trimmed(self):
        result = validate({"topic": "  claude-code  "})
        self.assertTrue(result["valid"])
        self.assertEqual(result["topic"], "claude-code")

    def test_topic_rejects_invalid_characters(self):
        result = validate({"topic": "claude/code"})
        self.assertFalse(result["valid"])
        self.assertIn("invalid characters", result["error"])

    def test_rejects_too_many_hints(self):
        hints = [f"h{i}" for i in range(11)]
        result = validate({"topic": "topic", "hints": hints})
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "hints exceeds 10 items")

    def test_rejects_overlong_hint(self):
        result = validate({"topic": "topic", "hints": ["a" * 51]})
        self.assertFalse(result["valid"])
        self.assertIn("exceeds 50 characters", result["error"])

    def test_since_window_requires_start_and_end(self):
        result = validate({"topic": "topic", "since_window": {"end_date": "2026-03-01"}})
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "since_window.start_date is required")

        result = validate({"topic": "topic", "since_window": {"start_date": "2026-03-01"}})
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "since_window.end_date is required")

    def test_since_window_rejects_invalid_dates(self):
        result = validate(
            {
                "topic": "topic",
                "since_window": {"start_date": "2026-02-31", "end_date": "2026-03-01"},
            }
        )
        self.assertFalse(result["valid"])
        self.assertIn("start_date is not a valid date", result["error"])

        result = validate(
            {
                "topic": "topic",
                "since_window": {"start_date": "2026-03-01", "end_date": "not-a-date"},
            }
        )
        self.assertFalse(result["valid"])
        self.assertIn("end_date is not a valid date", result["error"])

    def test_since_window_rejects_inverted_range(self):
        result = validate(
            {
                "topic": "topic",
                "since_window": {"start_date": "2026-03-07", "end_date": "2026-03-01"},
            }
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "since_window.start_date must not be after end_date")

    def test_since_window_rejects_future_start_date(self):
        with patch("validate_input.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 10)
            mock_date.fromisoformat.side_effect = date.fromisoformat
            result = validate(
                {
                    "topic": "topic",
                    "since_window": {"start_date": "2026-03-11", "end_date": "2026-03-12"},
                }
            )
        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "since_window.start_date cannot be in the future")


if __name__ == "__main__":
    unittest.main()
