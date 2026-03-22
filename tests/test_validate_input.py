"""Tests for validate_input.py"""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from validate_input import validate


class TestValidateTopic(unittest.TestCase):
    def test_valid_topic(self):
        r = validate("claude-code")
        self.assertTrue(r["valid"])
        self.assertEqual(r["topic"], "claude-code")

    def test_valid_topic_with_spaces(self):
        r = validate("ai agents")
        self.assertTrue(r["valid"])
        self.assertEqual(r["topic"], "ai agents")

    def test_empty_topic(self):
        self.assertFalse(validate("")["valid"])

    def test_whitespace_only_topic(self):
        self.assertFalse(validate("   ")["valid"])

    def test_topic_too_long(self):
        self.assertFalse(validate("a" * 101)["valid"])

    def test_topic_at_max_length(self):
        self.assertTrue(validate("a" * 100)["valid"])

    def test_topic_invalid_chars(self):
        self.assertFalse(validate("hello!")["valid"])
        self.assertFalse(validate("topic@domain")["valid"])
        self.assertFalse(validate("foo/bar")["valid"])

    def test_topic_strips_whitespace(self):
        r = validate("  claude-code  ")
        self.assertTrue(r["valid"])
        self.assertEqual(r["topic"], "claude-code")


class TestValidateHints(unittest.TestCase):
    def test_no_hints(self):
        r = validate("topic", "")
        self.assertTrue(r["valid"])
        self.assertEqual(r["hints"], [])

    def test_single_hint(self):
        r = validate("topic", "@karpathy")
        self.assertTrue(r["valid"])
        self.assertEqual(r["hints"], ["@karpathy"])

    def test_multiple_hints(self):
        r = validate("topic", "3blue1brown,@karpathy,lexfridman")
        self.assertTrue(r["valid"])
        self.assertEqual(len(r["hints"]), 3)

    def test_hints_deduplication(self):
        r = validate("topic", "a,b,a,c")
        self.assertTrue(r["valid"])
        self.assertEqual(r["hints"], ["a", "b", "c"])

    def test_too_many_hints(self):
        hints = ",".join(f"h{i}" for i in range(11))
        self.assertFalse(validate("topic", hints)["valid"])

    def test_hints_at_max_count(self):
        hints = ",".join(f"h{i}" for i in range(10))
        self.assertTrue(validate("topic", hints)["valid"])

    def test_hint_too_long(self):
        self.assertFalse(validate("topic", "a" * 51)["valid"])

    def test_hint_at_max_length(self):
        self.assertTrue(validate("topic", "a" * 50)["valid"])

    def test_hints_strips_whitespace(self):
        r = validate("topic", " a , b ")
        self.assertTrue(r["valid"])
        self.assertEqual(r["hints"], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
