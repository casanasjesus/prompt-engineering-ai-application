import sys
import os
import pytest

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_parser import IntentParser

@pytest.fixture
def sample_schema():
    return {
        "tables": [
            {
                "name": "Companies",
                "columns": [
                    {"name": "id"},
                    {"name": "industry"},
                ],
            },
            {
                "name": "Employees",
                "columns": [
                    {"name": "id"},
                    {"name": "salary"},
                    {"name": "department_id"},
                ],
            },
        ]
    }

# -------------------------
# SELECT
# -------------------------

def test_select_english(sample_schema):
    parser = IntentParser(sample_schema)
    intent = parser.parse("show employees")

    assert intent["action"] == "select"
    assert intent["table"] == "Employees"

def test_select_with_limit(sample_schema):
    parser = IntentParser(sample_schema)
    intent = parser.parse("top 5 employees")

    assert intent["limit"] == 5

# -------------------------
# COUNT
# -------------------------

def test_count_english(sample_schema):
    parser = IntentParser(sample_schema)
    intent = parser.parse("how many companies exist")

    assert intent["action"] == "count"
    assert intent["table"] == "Companies"

# -------------------------
# AGGREGATE
# -------------------------

def test_average_english(sample_schema):
    parser = IntentParser(sample_schema)
    intent = parser.parse("average salary by department_id")

    assert intent["action"] == "aggregate"
    assert intent["metric"] == "avg"
    assert intent["group_by"] == "department_id"

# -------------------------
# UNKNOWN
# -------------------------

def test_unknown_intent(sample_schema):
    parser = IntentParser(sample_schema)
    intent = parser.parse("anything")

    assert intent["action"] == "unknown"
    assert intent["table"] is None