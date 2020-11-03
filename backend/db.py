import sqlite3
from sqlite3 import Error
import pandas as pd


def create_connection(db_path):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        print("DB connection created.")
    except Error as e:
        print(e)

    return conn


def close_connection(conn):
    """ close a database connection to a SQLite database """
    conn.close()
    print("DB connection closed.")


def write_full_table(conn, table_name, df, index_label="pandas_index"):
    """ writes a dataframe to the database, fully replacing any existing table """
    df.to_sql(table_name, conn, if_exists="replace", index_label=index_label)


def read_full_table(conn, table_name, index_col="pandas_index"):
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn, index_col=index_col)
    print(f"Read {len(df)} lines from '{table_name}' table in DB.")
    return df


def read_last_index(conn, table_name, index_col="pandas_index"):
    last_index = pd.read_sql(f"SELECT MAX({index_col}) FROM {table_name}", conn)[
        f"MAX({index_col})"
    ].item()

    return last_index


def append_to_table(conn, table_name, df, index_label="pandas_index"):
    df.to_sql(table_name, conn, if_exists="append", index_label=index_label)


def check_if_table_exists(conn, table_name):
    c = conn.cursor()
    c.execute(
        f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )

    if c.fetchone()[0] == 1:
        return True
    else:
        return False
