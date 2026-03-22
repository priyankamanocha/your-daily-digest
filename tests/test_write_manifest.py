"""Tests for write_manifest.py."""
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from write_manifest import derive_manifest_path
from temp_utils import make_temp_dir, remove_temp_dir


SCRIPT = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".claude",
    "skills",
    "daily-digest",
    "scripts",
    "write_manifest.py",
)


class TestDeriveManifestPath(unittest.TestCase):
    def test_derives_sidecar_path(self):
        self.assertEqual(
            derive_manifest_path("digests/2026/03/digest-2026-03-22-topic.md"),
            "digests/2026/03/digest-2026-03-22-topic.manifest.json",
        )

    def test_rejects_non_markdown_path(self):
        with self.assertRaises(ValueError):
            derive_manifest_path("digests/2026/03/digest.txt")


class TestWriteManifestCli(unittest.TestCase):
    def _run(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_writes_manifest_file(self):
        tmp = make_temp_dir()
        try:
            digest_path = os.path.join(tmp, "digests", "2026", "03", "digest-2026-03-22-topic.md")
            payload = json.dumps({"schema_version": "1.0", "topic": "topic"})
            result = self._run(digest_path, payload, cwd=tmp)

            manifest_path = os.path.join(tmp, "digests", "2026", "03", "digest-2026-03-22-topic.manifest.json")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(manifest_path))
            with open(manifest_path, encoding="utf-8") as handle:
                self.assertEqual(json.load(handle), {"schema_version": "1.0", "topic": "topic"})
        finally:
            remove_temp_dir(tmp)

    def test_invalid_json_exits_nonzero(self):
        tmp = make_temp_dir()
        try:
            digest_path = os.path.join(tmp, "digest.md")
            result = self._run(digest_path, "{not-json}", cwd=tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not valid JSON", result.stderr)

    def test_non_markdown_digest_path_exits_nonzero(self):
        tmp = make_temp_dir()
        try:
            result = self._run("digest.txt", json.dumps({"ok": True}), cwd=tmp)
        finally:
            remove_temp_dir(tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must end with .md", result.stderr)


if __name__ == "__main__":
    unittest.main()
