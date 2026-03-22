"""Tests for load_source_filters.py."""
import json
import os
import subprocess
import sys
import unittest

from temp_utils import make_temp_dir, remove_temp_dir


SCRIPT = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".claude",
    "skills",
    "daily-digest",
    "scripts",
    "load_source_filters.py",
)


class TestLoadSourceFilters(unittest.TestCase):
    def _run(self, cwd):
        return subprocess.run(
            [sys.executable, SCRIPT],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_missing_file_returns_exit_2(self):
        tmp = make_temp_dir()
        try:
            result = self._run(tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout), {"filter_config": None})

    def test_valid_config_loads(self):
        tmp = make_temp_dir()
        try:
            with open(os.path.join(tmp, "sources.json"), "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "global": {"allow": ["example.com"], "block": ["spam.com"]},
                        "topics": {"ai-agents": {"allow": ["anthropic.com"]}},
                    },
                    handle,
                )
            result = self._run(tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["filter_config"]["global"]["allow"], ["example.com"])
        self.assertEqual(payload["filter_config"]["topics"]["ai-agents"]["allow"], ["anthropic.com"])

    def test_invalid_json_returns_error(self):
        tmp = make_temp_dir()
        try:
            with open(os.path.join(tmp, "sources.json"), "w", encoding="utf-8") as handle:
                handle.write("{ invalid json")
            result = self._run(tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid JSON", json.loads(result.stdout)["error"])

    def test_rejects_non_string_entries(self):
        tmp = make_temp_dir()
        try:
            with open(os.path.join(tmp, "sources.json"), "w", encoding="utf-8") as handle:
                json.dump({"global": {"allow": ["good.com", 123]}}, handle)
            result = self._run(tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("array of strings", json.loads(result.stdout)["error"])


if __name__ == "__main__":
    unittest.main()
