#!/usr/bin/env python3

"""filebox2 is the evolution of filebox that supports file groups"""

import sqlite3


GROUPS_TABLE = "groups"
FILES_TABLE = "files"


class FileBox2:
    """
    Store/retrieve groups of files to/from an sqlite database
    """

    def __init__(self, name):
        """
        Args:

            name (str): filebox name
        """
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()
        query = (
            "CREATE TABLE IF NOT EXISTS {} "
            "(id INTEGER PRIMARY KEY,"
            " name VARCHAR UNIQUE)"
        ).format(GROUPS_TABLE)
        self.cursor.execute(query)
        query = (
            "CREATE TABLE IF NOT EXISTS {} "
            "(id INTEGER PRIMARY KEY,"
            " gid INTEGER,"
            " name VARCHAR,"
            " data BLOB)"
        ).format(FILES_TABLE)
        self.cursor.execute(query)
        self.conn.commit()

    def get_group_id(self, group_name):
        """
        Find group id by name

        Args:
            group_name (str): group name

        Return: int
        """
        query = (
            "SELECT id FROM {} "
            "WHERE name=?"
        ).format(GROUPS_TABLE)
        self.cursor.execute(query, (group_name,))
        row = self.cursor.fetchone()
        group_id = row[0]
        return group_id

    def put_group(self, group_name):
        """
        Create a group in the database

        Args:
            group_name (str) - group name

        """
        query = ("INSERT INTO {}(name) " "VALUES(?)").format(GROUPS_TABLE)
        self.cursor.execute(query, (group_name,),)
        self.conn.commit()

    def ls_groups(self):
        """
        List group names

        Return: list
        """
        query = (
            "SELECT name FROM {}"
        ).format(GROUPS_TABLE)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        group_names = [x[0] for x in rows]
        return group_names

    def rm_group(self, group_name):
        """
        Remove a group from the filebox
        (and all the files belonging to it as well)

        Args:
            group_name (str): group name
        """
        group_id = self.get_group_id(group_name)
        query = (
            "DELETE FROM {} "
            "WHERE gid=?"
        ).format(FILES_TABLE)
        self.cursor.execute(query, (group_id,))
        query = (
            "DELETE FROM {} "
            "WHERE id=?"
        ).format(GROUPS_TABLE)
        self.cursor.execute(query, (group_id,))
        self.conn.commit()

    def put_file(self, group_name, fs_filename, filename):
        """
        Save a file from disk to the filebox

        Content of `fs_filename` is read and saved to the filebox as
        `filename`

        Args:
            group_name (str): group name

            fs_filename (str): file name on the filesystem to save content to

            filename (str): file name
        """
        group_id = self.get_group_id(group_name)
        query = ("INSERT INTO {}(gid, name, data) " "VALUES(?, ?, ?)").format(FILES_TABLE)
        with open(fs_filename, "rb") as f:
            self.cursor.execute(
                query,
                (
                    group_id,
                    filename,
                    f.read(),
                ),
            )
        self.conn.commit()

    def get_file(self, group_name, filename, fs_filename):
        """
        Get a file content from the filebox

        Args:
            group_name (str): group name

            filename (str): file name

            fs_filename (str): file name on the filesystem to save content to
        """
        query = (
            "SELECT files.name, files.data "
            "FROM {} "
            "JOIN {} ON "
            "groups.name = ? AND "
            "groups.id = files.gid AND "
            "files.name = ?"
        ).format(FILES_TABLE, GROUPS_TABLE)
        self.cursor.execute(query, (group_name, filename,))
        row = self.cursor.fetchone()
        data = row[1]
        with open(fs_filename, "wb") as f:
            f.write(data)

    def rm_file(self, filename):
        """
        Remove a file from the filebox

        Args:
            filename (str): file name
        """
        query = (
            "DELETE FROM {} "
            "WHERE name=?"
        ).format(FILES_TABLE)
        self.cursor.execute(query, (filename,))
        self.conn.commit()


def filebox2(name):
    """
    Factory method that returns a filebox2 object

    Args:

        name (str): filebox2 name

    Return: FileBox2 object
    """
    return FileBox2(name)
