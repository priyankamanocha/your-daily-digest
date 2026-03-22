"""Tests for diff_digest.py."""
import os
import sys
import unittest
from datetime import date
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from diff_digest import _parse_sections, find_baseline
from temp_utils import make_temp_dir, remove_temp_dir


class TestParseSections(unittest.TestCase):
    def test_extracts_titles_from_all_sections(self):
        content = """# Daily Digest - Topic

Generated: 2026-03-21 08:00
Discovery: complete

## Key Insights (1-3)

### Insight One
Details

### Insight Two
More details

## Anti-patterns (2-4)

- **Pattern One**: Avoid this.
- **Pattern Two**: Avoid that.

## Actions to Try (1-3)

### Action One
- Effort: low

## Resources (3-5)

- **Resource One**: https://example.com
"""
        sections = _parse_sections(content)
        self.assertEqual(sections["key_insights"], ["Insight One", "Insight Two"])
        self.assertEqual(sections["anti_patterns"], ["Pattern One", "Pattern Two"])
        self.assertEqual(sections["actions"], ["Action One"])
        self.assertEqual(sections["resources"], ["Resource One"])


class TestFindBaseline(unittest.TestCase):
    def setUp(self):
        self.tmp = make_temp_dir()
        self.orig_cwd = os.getcwd()
        os.chdir(self.tmp)
        os.makedirs(os.path.join("digests", "2026", "03"), exist_ok=True)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        remove_temp_dir(self.tmp)

    def _write_digest(self, day, slug, body="### Fresh Insight\nBody\n"):
        path = os.path.join("digests", "2026", "03", f"digest-2026-03-{day:02d}-{slug}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(
                "# Daily Digest - Topic\n\n"
                "Generated: 2026-03-01 08:00\n"
                "Discovery: complete\n\n"
                "## Key Insights (1-3)\n\n"
                f"{body}\n"
                "## Anti-patterns (2-4)\n\n"
                "- **Pattern**: Avoid it.\n\n"
                "## Actions to Try (1-3)\n\n"
                "### Action\n"
                "- Effort: low\n\n"
                "## Resources (3-5)\n\n"
                "- **Resource**: https://example.com\n"
            )
        return path

    def test_returns_most_recent_prior_digest_within_window(self):
        older = self._write_digest(18, "claude-code", "### Older Insight\nBody\n")
        newer = self._write_digest(20, "claude-code", "### Newer Insight\nBody\n")
        self._write_digest(21, "claude-code", "### Today Insight\nBody\n")

        with patch("diff_digest.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 21)
            result = find_baseline("claude-code", 7)

        self.assertTrue(result["found"])
        self.assertEqual(result["baseline_date"], "2026-03-20")
        self.assertTrue(result["baseline_path"].endswith(newer.replace("\\", "/")))
        self.assertEqual(result["sections"]["key_insights"], ["Newer Insight"])
        self.assertNotIn(older.replace("\\", "/"), result["baseline_path"])

    def test_returns_not_found_when_only_digest_is_stale(self):
        self._write_digest(10, "claude-code")
        with patch("diff_digest.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 21)
            result = find_baseline("claude-code", 7)
        self.assertEqual(result, {"found": False})

    def test_returns_not_found_for_empty_baseline_file(self):
        path = os.path.join("digests", "2026", "03", "digest-2026-03-20-claude-code.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("   ")
        with patch("diff_digest.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 21)
            result = find_baseline("claude-code", 7)
        self.assertEqual(result, {"found": False})


if __name__ == "__main__":
    unittest.main()
