"""Helpers for creating writable temp directories inside the repo workspace."""
import os
import shutil
import tempfile


REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
TEST_TMP_ROOT = os.path.join(REPO_ROOT, ".test_tmp")
os.makedirs(TEST_TMP_ROOT, exist_ok=True)


def make_temp_dir():
    return tempfile.mkdtemp(dir=TEST_TMP_ROOT)


def remove_temp_dir(path):
    shutil.rmtree(path, ignore_errors=True)
