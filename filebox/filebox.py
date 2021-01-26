#!/usr/bin/env python3

"""filebox is a simple API that lets you store/retrieve files to/from an sqlite
database"""

import sqlite3


FILES_TABLE = "files"


class FileBox:
    """
    Store/retrieve files to/from an sqlite database
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
            "(id INTEGER PRIMARY KEY, "
            " name VARCHAR UNIQUE, "
            " data BLOB)"
        ).format(FILES_TABLE)
        self.cursor.execute(query)
        self.conn.commit()

    def put(self, fs_filename, filename):
        """
        Save a file from disk to the filebox

        Content of `fs_filename` is read and saved to the filebox as
        `filename`

        Args:
            fs_filename (str): file name on the filesystem to save content to

            filename (str): file name
        """
        query = ("INSERT INTO {}(name, data) " "VALUES(?, ?)").format(FILES_TABLE)
        with open(fs_filename, "rb") as f:
            self.cursor.execute(
                query,
                (
                    filename,
                    f.read(),
                ),
            )
        self.conn.commit()

    def get(self, filename, fs_filename):
        """
        Get a file content from the filebox

        Args:
            filename (str): file name

            fs_filename (str): file name on the filesystem to save content to
        """
        query = ("SELECT name, data FROM {} " "WHERE name=?").format(FILES_TABLE)
        self.cursor.execute(query, (filename,))
        row = self.cursor.fetchone()
        data = row[1]
        with open(fs_filename, "wb") as f:
            f.write(data)


def filebox(name):
    """
    Factory method that returns a filebox object

    Args:

        name (str): filebox name

    Return: FileBox object
    """
    return FileBox(name)
