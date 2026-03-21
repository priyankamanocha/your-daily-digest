"""Tests for write_digest.py"""
import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from write_digest import write_digest


class TestWriteDigest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_file_with_content(self):
        path = os.path.join(self.tmp.name, "digest.md")
        write_digest(path, "hello world")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "hello world")

    def test_creates_intermediate_directories(self):
        path = os.path.join(self.tmp.name, "2026", "03", "digest.md")
        write_digest(path, "content")
        self.assertTrue(os.path.exists(path))

    def test_overwrites_existing_file(self):
        path = os.path.join(self.tmp.name, "digest.md")
        write_digest(path, "first")
        write_digest(path, "second")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "second")

    def test_utf8_content(self):
        path = os.path.join(self.tmp.name, "digest.md")
        content = "⚠️ Low-signal content — insights below"
        write_digest(path, content)
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), content)

    def test_empty_content(self):
        path = os.path.join(self.tmp.name, "digest.md")
        write_digest(path, "")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "")


if __name__ == "__main__":
    unittest.main()
