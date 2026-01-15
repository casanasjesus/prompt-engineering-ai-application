import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.sql_query_builder import SQLQueryBuilder


@pytest.fixture
def builder():
    return SQLQueryBuilder()


# -------------------------
# SELECT
# -------------------------

def test_select_basic(builder):
    intent = {
        "action": "select",
        "table": "Employees",
        "limit": 5,
    }

    sql = builder.build(intent)
    assert sql == "SELECT * FROM Employees LIMIT 5;"


def test_select_without_limit(builder):
    intent = {
        "action": "select",
        "table": "Companies",
        "limit": None,
    }

    sql = builder.build(intent)
    assert sql == "SELECT * FROM Companies;"


# -------------------------
# COUNT
# -------------------------

def test_count(builder):
    intent = {
        "action": "count",
        "table": "Employees",
    }

    sql = builder.build(intent)
    assert sql == "SELECT COUNT(*) FROM Employees;"


# -------------------------
# AGGREGATE
# -------------------------

def test_average_with_group_by(builder):
    intent = {
        "action": "aggregate",
        "table": "Employees",
        "metric": "avg",
        "group_by": "department_id",
    }

    sql = builder.build(intent)
    assert sql == (
        "SELECT department_id, AVG(*) FROM Employees GROUP BY department_id;"
    )


def test_average_without_group_by(builder):
    intent = {
        "action": "aggregate",
        "table": "Employees",
        "metric": "avg",
        "group_by": None,
    }

    sql = builder.build(intent)
    assert sql == "SELECT AVG(*) FROM Employees;"
