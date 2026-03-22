"""Tests for check_runtime.py"""
import sys
import os
import unittest
from unittest.mock import patch
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".claude", "skills", "daily-digest", "scripts"))
from check_runtime import check_python_version, check_digests_writable


class TestCheckPythonVersion(unittest.TestCase):
    def test_current_version_passes(self):
        ok, msg = check_python_version()
        self.assertTrue(ok)
        self.assertIn("ok", msg)

    def test_python_27_fails(self):
        with patch("check_runtime.sys") as mock_sys:
            mock_sys.version_info = (2, 7)
            ok, msg = check_python_version()
        self.assertFalse(ok)
        self.assertIn("2.7", msg)

    def test_python_37_fails(self):
        with patch("check_runtime.sys") as mock_sys:
            mock_sys.version_info = (3, 7)
            ok, msg = check_python_version()
        self.assertFalse(ok)

    def test_python_38_passes(self):
        with patch("check_runtime.sys") as mock_sys:
            mock_sys.version_info = (3, 8)
            ok, _ = check_python_version()
        self.assertTrue(ok)

    def test_python_310_passes(self):
        with patch("check_runtime.sys") as mock_sys:
            mock_sys.version_info = (3, 10)
            ok, _ = check_python_version()
        self.assertTrue(ok)


class TestCheckDigestsWritable(unittest.TestCase):
    def test_writable_directory_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "digests")
            with patch("check_runtime.Path") as mock_path_cls:
                mock_path_cls.return_value = _FakePath(target)
                ok, msg = check_digests_writable()
        self.assertTrue(ok)
        self.assertIn("writable", msg)

    def test_unwritable_directory_fails(self):
        with patch("check_runtime.Path") as mock_path_cls:
            mock_path_cls.return_value = _ErrorPath()
            ok, msg = check_digests_writable()
        self.assertFalse(ok)
        self.assertIn("not writable", msg)


class _FakePath:
    """A writable fake path backed by a real temp dir."""
    def __init__(self, real_dir):
        self._dir = real_dir
        self._probe = os.path.join(real_dir, ".write_probe")

    def mkdir(self, **kwargs):
        os.makedirs(self._dir, exist_ok=True)

    def __truediv__(self, name):
        return _FakeProbe(os.path.join(self._dir, name))


class _FakeProbe:
    def __init__(self, path):
        self._path = path

    def write_text(self, content):
        with open(self._path, "w") as f:
            f.write(content)

    def unlink(self):
        os.unlink(self._path)


class _ErrorPath:
    """A path that always raises OSError."""
    def mkdir(self, **kwargs):
        raise OSError("permission denied")

    def __truediv__(self, name):
        return self


if __name__ == "__main__":
    unittest.main()
