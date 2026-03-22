"""Tests for write_digest.py."""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from write_digest import write_digest
from temp_utils import make_temp_dir, remove_temp_dir


class TestWriteDigest(unittest.TestCase):
    def setUp(self):
        self.tmp = make_temp_dir()

    def tearDown(self):
        remove_temp_dir(self.tmp)

    def test_creates_file_with_content(self):
        path = os.path.join(self.tmp, "digest.md")
        write_digest(path, "hello world")
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "hello world")

    def test_creates_intermediate_directories(self):
        path = os.path.join(self.tmp, "2026", "03", "digest.md")
        write_digest(path, "content")
        self.assertTrue(os.path.exists(path))

    def test_overwrites_existing_file(self):
        path = os.path.join(self.tmp, "digest.md")
        write_digest(path, "first")
        write_digest(path, "second")
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "second")

    def test_utf8_content(self):
        path = os.path.join(self.tmp, "digest.md")
        content = "Low-signal content - insights below"
        write_digest(path, content)
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), content)

    def test_empty_content(self):
        path = os.path.join(self.tmp, "digest.md")
        write_digest(path, "")
        with open(path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "")


if __name__ == "__main__":
    unittest.main()
