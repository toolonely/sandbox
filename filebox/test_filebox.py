"""tests for filebox module"""

import hashlib
import os

import pytest

import filebox


FILEBOX = "filebox"
DBNAME = "{}.sqlite".format(FILEBOX)
FILENAME = "file"
TEXT = "foo"
NEW_FILENAME = "new{}".format(FILENAME)


@pytest.fixture(scope="session")
def tmp(tmpdir_factory):
    """generate a tempdir name"""
    return tmpdir_factory.mktemp(FILEBOX)

@pytest.fixture(scope="session")
def a_filebox(tmp):
    abs_file_name = os.path.join(tmp, DBNAME)
    if os.path.isfile(abs_file_name):
        os.unlink(abs_file_name)
    return abs_file_name


@pytest.fixture(scope="session")
def a_file(tmp):
    filename = FILENAME
    abs_file_name = os.path.join(tmp, filename)
    if os.path.isfile(abs_file_name):
        os.unlink(abs_file_name)
    else:
        with open(abs_file_name, "w") as f:
            f.write(TEXT)
    return abs_file_name


def sha256(filename):
    """
    Compute the SHA256 checksum for a file

    Args:
        filename (str) - file name

    Return: string
    """
    chunk_size = 1024
    with open(filename, "rb") as f:
        file_hash = hashlib.sha256()
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            file_hash.update(chunk)
    return file_hash.hexdigest()


@pytest.fixture(scope="session")
def a_sha256(a_file):
    return sha256(a_file)


class TestFilebox:
    def test_get_and_put(self, tmp, a_filebox, a_file, a_sha256):
        box = filebox.filebox(a_filebox)
        box.put(a_file, os.path.basename(a_file))
        new_abs_file_name = os.path.join(tmp, NEW_FILENAME)
        box.get(os.path.basename(a_file), new_abs_file_name)
        assert a_sha256 == sha256(new_abs_file_name)
