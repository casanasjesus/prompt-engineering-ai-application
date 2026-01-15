import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.query_executor import QueryExecutor

def test_execute_select():
    connection_params = {"host": "x"}

    mock_cursor = MagicMock()
    mock_cursor.description = True
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "John"},
        {"id": 2, "name": "Jane"},
    ]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    with patch("psycopg2.connect", return_value=mock_conn):
        executor = QueryExecutor(connection_params)
        result = executor.execute("SELECT * FROM users")

    assert len(result) == 2
    assert result[0]["name"] == "John"

def test_execute_non_select():
    connection_params = {"host": "x"}

    mock_cursor = MagicMock()
    mock_cursor.description = None

    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    with patch("psycopg2.connect", return_value=mock_conn):
        executor = QueryExecutor(connection_params)
        result = executor.execute("UPDATE users SET active = true")

    assert result is None

