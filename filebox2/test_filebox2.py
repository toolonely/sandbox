"""tests for filebox module"""

import hashlib
import os
import sqlite3

import pytest

import filebox2


FILEBOX = "filebox2"
GROUP_NAME1 = "group1"
FILENAME = "file"
TEXT = "foo"
NEW_FILENAME = "new{}".format(FILENAME)


@pytest.fixture(scope="session")
def tmp(tmpdir_factory):
    """generate a tempdir name"""
    return tmpdir_factory.mktemp(FILEBOX)


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


class TestFilebox2:
    def test_get_group_id(self, tmp):
        box = filebox2.filebox2(":memory:")
        with pytest.raises(TypeError):  # fetchone() returns None
            box.get_group_id(GROUP_NAME1)

    def test_ls_and_put_group(self, tmp):
        box = filebox2.filebox2(":memory:")
        assert box.ls_groups() == []
        box.put_group(GROUP_NAME1)
        assert box.ls_groups() == [GROUP_NAME1]

    def test_rm_group(self, tmp):
        # WARNING: not atopic! uses the state of the filebox after test_ls_and_put_group()
        box = filebox2.filebox2(":memory:")
        box.put_group(GROUP_NAME1)
        box.rm_group(GROUP_NAME1)
        assert box.ls_groups() == []
        # TODO: write test for removing non-empty group, after writing tests for files

    def test_get_file_and_put_file(self, tmp, a_file, a_sha256):
        box = filebox2.filebox2(":memory:")
        box.put_group(GROUP_NAME1)
        box.put_file(GROUP_NAME1, a_file, os.path.basename(a_file))
        new_abs_file_name = os.path.join(tmp, NEW_FILENAME)
        box.get_file(GROUP_NAME1, os.path.basename(a_file), new_abs_file_name)
        assert a_sha256 == sha256(new_abs_file_name)
