import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.nl_to_sql_pipeline import NLToSQLPipeline


def sample_schema():
    return {
        "tables": [
            {
                "name": "Employees",
                "columns": [
                    {"name": "id"},
                    {"name": "salary"},
                ],
            }
        ]
    }


def test_pipeline_select():
    schema = sample_schema()
    connection_params = {"host": "x"}

    with patch("src.nl_to_sql_pipeline.IntentParser") as MockParser, \
         patch("src.nl_to_sql_pipeline.SQLQueryBuilder") as MockBuilder, \
         patch("src.nl_to_sql_pipeline.QueryExecutor") as MockExecutor:

        mock_parser = MockParser.return_value
        mock_parser.parse.return_value = {
            "action": "select",
            "table": "Employees",
            "limit": 10,
        }

        mock_builder = MockBuilder.return_value
        mock_builder.build.return_value = "SELECT * FROM Employees LIMIT 10"

        mock_executor = MockExecutor.return_value
        mock_executor.execute.return_value = [
            {"id": 1, "salary": 1000},
            {"id": 2, "salary": 1200},
        ]

        pipeline = NLToSQLPipeline(schema, connection_params)
        response = pipeline.run("show employees")

        assert response["sql"] == "SELECT * FROM Employees LIMIT 10"
        assert len(response["result"]) == 2
        assert response["intent"]["action"] == "select"


def test_pipeline_unknown_intent():
    schema = sample_schema()
    connection_params = {"host": "x"}

    with patch("src.nl_to_sql_pipeline.IntentParser") as MockParser:
        mock_parser = MockParser.return_value
        mock_parser.parse.return_value = {
            "action": "unknown",
            "table": None,
        }

        pipeline = NLToSQLPipeline(schema, connection_params)
        response = pipeline.run("asdf qwer")

        assert response["sql"] is None
        assert response["result"] is None
        assert response["intent"]["action"] == "unknown"
