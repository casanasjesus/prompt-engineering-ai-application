import re

class IntentParser:
    def __init__(self, schema: dict):
        """
        schema: dict generado por schema_converter
        """
        self.schema = schema
        self.tables = {t["name"].lower(): t for t in schema["tables"]}

    def parse(self, text: str) -> dict:
        text = text.lower().strip()

        if self._is_count(text):
            return self._build_count_intent(text)

        if self._is_aggregate(text):
            return self._build_aggregate_intent(text)

        if self._is_select(text):
            return self._build_select_intent(text)

        return self._empty_intent("unknown")

    # ------------------------
    # Intent detectors
    # ------------------------

    def _is_select(self, text: str) -> bool:
        return any(word in text for word in ["show", "list", "display", "top", "limit"])

    def _is_count(self, text: str) -> bool:
        return any(word in text for word in ["count", "how many"])

    def _is_aggregate(self, text: str) -> bool:
        return any(word in text for word in ["average", "avg", "max", "min", "suma", "sum"])

    # ------------------------
    # Intent builders
    # ------------------------

    def _build_select_intent(self, text: str) -> dict:
        return {
            "action": "select",
            "table": self._extract_table(text),
            "columns": None,
            "filters": [],
            "limit": self._extract_limit(text),
            "group_by": None,
            "metric": None,
        }

    def _build_count_intent(self, text: str) -> dict:
        return {
            "action": "count",
            "table": self._extract_table(text),
            "columns": None,
            "filters": [],
            "limit": None,
            "group_by": None,
            "metric": None,
        }

    def _build_aggregate_intent(self, text: str) -> dict:
        metric = self._extract_metric(text)

        return {
            "action": "aggregate",
            "table": self._extract_table(text),
            "columns": None,
            "filters": [],
            "limit": None,
            "group_by": self._extract_group_by(text),
            "metric": metric,
        }

    # ------------------------
    # Extractors
    # ------------------------

    def _extract_table(self, text: str):
        for table_name in self.tables.keys():
            if table_name in text:
                return self.tables[table_name]["name"]
        return None

    def _extract_limit(self, text: str):
        match = re.search(r"(top|limit)\s+(\d+)", text)
        if match:
            return int(match.group(2))
        return 10

    def _extract_metric(self, text: str):
        if "average" in text or "avg" in text:
            return "avg"
        if "max" in text:
            return "max"
        if "min" in text:
            return "min"
        if "sum" in text:
            return "sum"
        return None

    def _extract_group_by(self, text: str):
        match = re.search(r"by\s+([\w_]+)", text)
        if not match:
            return None

        candidate = match.group(1)

        for table in self.schema["tables"]:
            for column in table["columns"]:
                if column["name"].lower() == candidate:
                    return column["name"]

        return None

    # ------------------------

    def _empty_intent(self, action: str):
        return {
            "action": action,
            "table": None,
            "columns": None,
            "filters": [],
            "limit": None,
            "group_by": None,
            "metric": None,
        }