import sqlite3
from sqlite3 import Error

import pandas as pd


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def __enter__(self):
        """Create a database connection to a SQLite database.
        Creates one if it does not exist."""
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_path)
        except Error as e:
            print(e)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Close a database connection to a SQLite database. """
        self.conn.close()

    def write_full_table(self, table, df, index_label="pandas_index"):
        """ Writes a dataframe to the database, fully replacing any existing table. """
        df.to_sql(table, self.conn, if_exists="replace", index_label=index_label)
        print(f"Wrote {len(df)} lines to '{table} table in DB")

    def read_full_table(self, table, index_col="pandas_index"):
        """ Reads full table from the DB. """
        df = pd.read_sql(f"SELECT * FROM {table}", self.conn, index_col=index_col)
        print(f"Read {len(df)} lines from '{table}' table in DB.")
        return df

    def read_last_index(self, table, index_col="pandas_index"):
        """ Reads last index that exists in specified table. """
        last_index = pd.read_sql(f"SELECT MAX({index_col}) FROM {table}", self.conn)[
            f"MAX({index_col})"
        ].item()

        return last_index

    def append_to_table(self, table, df, index_label="pandas_index"):
        """ Appends provided dataframe to the specified table in the DB. """
        df.to_sql(table, self.conn, if_exists="append", index_label=index_label)

    def check_if_table_exists(self, table):
        """ Checks if the table exists in the DB. """
        c = self.conn.cursor()
        c.execute(
            f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table}'"
        )

        if c.fetchone()[0] == 1:
            return True
        else:
            return False

    def read_column_as_list(self, table, column):
        """ Read single column from specified table and returns it as a list. """
        c = self.conn.cursor()
        c.execute(f"SELECT {column} FROM {table}")

        result = []
        for row in c.fetchall():
            result.append(row[0])

        return result
