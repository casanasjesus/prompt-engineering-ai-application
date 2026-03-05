import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "database" / "data_assistant.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def create_table_if_not_exists(table_name: str, rows: list):
    """
    Creates table dynamically based on JSON keys.
    """
    if not rows:
        return

    connection = get_connection()
    cursor = connection.cursor()

    columns = rows[0].keys()

    column_defs = ", ".join([f"{col} TEXT" for col in columns])

    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {column_defs}
    )
    """

    cursor.execute(query)
    connection.commit()
    connection.close()

def insert_rows(table_name: str, rows: list):
    if not rows:
        return

    connection = get_connection()
    cursor = connection.cursor()

    columns = rows[0].keys()
    placeholders = ", ".join(["?"] * len(columns))

    query = f"""
    INSERT INTO {table_name} ({", ".join(columns)})
    VALUES ({placeholders})
    """

    values = [tuple(row[col] for col in columns) for row in rows]

    cursor.executemany(query, values)

    connection.commit()
    connection.close()

def run_query(sql: str):
    connection = get_connection()

    df = pd.read_sql_query(sql, connection)

    connection.close()

    return df