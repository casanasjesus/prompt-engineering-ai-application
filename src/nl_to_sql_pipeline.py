from src.intent_parser import IntentParser
from src.sql_query_builder import SQLQueryBuilder
from src.query_executor import QueryExecutor

class NLToSQLPipeline:
    def __init__(self, schema: dict, connection_params: dict):
        self.intent_parser = IntentParser(schema)
        self.query_builder = SQLQueryBuilder()
        self.query_executor = QueryExecutor(connection_params)

    def run(self, text: str) -> dict:
        # 1. Parse intent
        intent = self.intent_parser.parse(text)

        if intent["action"] == "unknown":
            return {
                "intent": intent,
                "sql": None,
                "result": None,
                "explanation": "Sorry, I could not understand your request.",
            }

        # 2. Build SQL
        sql = self.query_builder.build(intent)

        # 3. Execute SQL
        result = self.query_executor.execute(sql)

        # 4. Build explanation
        explanation = self._build_explanation(intent, result)

        return {
            "intent": intent,
            "sql": sql,
            "result": result,
            "explanation": explanation,
        }

    def _build_explanation(self, intent: dict, result):
        action = intent["action"]

        if action == "select":
            count = len(result) if result else 0
            return f"Showing {count} rows from {intent['table']}."

        if action == "count":
            if result and len(result) > 0:
                value = list(result[0].values())[0]
                return f"There are {value} rows in {intent['table']}."
            return "No results found."

        if action == "aggregate":
            return "Aggregation result returned."

        return "Query executed."
