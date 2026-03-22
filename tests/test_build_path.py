"""Tests for build_path.py"""
import sys
import os
import unittest
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from build_path import build_path

FIXED_NOW = datetime(2026, 3, 21, 14, 30, 0)


class TestBuildPath(unittest.TestCase):
    def _build(self, topic):
        with patch("build_path.datetime") as mock_dt:
            mock_dt.now.return_value = FIXED_NOW
            return build_path(topic)

    def test_path_format(self):
        path = self._build("claude-code")
        self.assertEqual(path, "digests/2026/03/digest-2026-03-21-claude-code.md")

    def test_spaces_become_hyphens(self):
        path = self._build("ai agents")
        self.assertIn("ai-agents", path)

    def test_uppercase_lowercased(self):
        path = self._build("Claude-Code")
        self.assertIn("claude-code", path)

    def test_special_chars_stripped(self):
        path = self._build("hello! world@2026")
        self.assertIn("hello-world2026", path)

    def test_slug_truncated_at_50(self):
        long_topic = "a" * 60
        path = self._build(long_topic)
        slug = path.split("digest-2026-03-21-")[1].replace(".md", "")
        self.assertLessEqual(len(slug), 50)

    def test_year_month_in_path(self):
        path = self._build("topic")
        self.assertTrue(path.startswith("digests/2026/03/"))

    def test_ends_with_md(self):
        self.assertTrue(self._build("topic").endswith(".md"))


if __name__ == "__main__":
    unittest.main()
