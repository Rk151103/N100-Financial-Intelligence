"""
src/utils/helpers.py

Common helper functions for
N100 Financial Intelligence Platform.
"""

from pathlib import Path
import sqlite3
import pandas as pd

# -------------------------------------------------------
# Project Paths
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# -------------------------------------------------------
# Database
# -------------------------------------------------------

def get_connection():
    """
    Return SQLite connection.
    """
    return sqlite3.connect(DB_PATH)


def execute_query(query, params=None):
    """
    Execute SQL query and return DataFrame.
    """

    conn = get_connection()

    if params is None:
        params = ()

    df = pd.read_sql_query(
        query,
        conn,
        params=params
    )

    conn.close()

    return df


def get_table(table_name):
    """
    Read complete database table.
    """

    return execute_query(
        f"SELECT * FROM {table_name}"
    )


# -------------------------------------------------------
# Files
# -------------------------------------------------------

def save_csv(df, filename):
    """
    Save dataframe into output folder.
    """

    path = OUTPUT_DIR / filename

    df.to_csv(
        path,
        index=False
    )

    return path


def load_csv(path):
    """
    Load CSV file.
    """

    return pd.read_csv(path)


# -------------------------------------------------------
# Formatting
# -------------------------------------------------------

def safe_divide(a, b):
    """
    Divide safely.
    """

    if pd.isna(a):
        return None

    if pd.isna(b):
        return None

    if b == 0:
        return None

    return round(a / b, 4)


def format_number(value):

    if pd.isna(value):
        return "-"

    return f"{value:,.2f}"


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

def table_exists(table):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
        """,
        (table,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# -------------------------------------------------------
# Demo
# -------------------------------------------------------

if __name__ == "__main__":

    print("Database Exists :", DB_PATH.exists())

    print("Companies Table :", table_exists("companies"))

    print("Profit Table :", table_exists("profitandloss"))