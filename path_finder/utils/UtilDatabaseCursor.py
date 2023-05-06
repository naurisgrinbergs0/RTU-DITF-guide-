import sqlite3
import os
import sys

class UtilDatabaseCursor:

    def __init__(self): # instance = UtilDatabaseCursor()
        super().__init__()
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "database", "project_map.sqlite"))
        self.cursor = None

    def __enter__(self): # with instance as something:
        self.conn.__enter__()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, *args, **kwargs):
        print("pretend to be a function")

