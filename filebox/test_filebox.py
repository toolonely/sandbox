"""tests for filebox module"""

import hashlib
import os
import sqlite3

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

    def test_double_put(self, tmp, a_filebox, a_file):
        """
        a file can't be saved twice into the filebox
        there's no need to save it twoce since the database has session scope
        and one record is already there
        """
        box = filebox.filebox(a_filebox)
        with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed"):
            # eww, an eight years old bug
            # https://bugs.python.org/issue16379
            box.put(a_file, os.path.basename(a_file))
