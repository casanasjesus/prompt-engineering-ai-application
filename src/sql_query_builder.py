class SQLQueryBuilder:
    """
    Construye consultas SQL (PostgreSQL) a partir de intents estructurados.
    """

    def build(self, intent: dict) -> str:
        action = intent.get("action")

        if action == "select":
            return self._build_select(intent)

        if action == "count":
            return self._build_count(intent)

        if action == "aggregate":
            return self._build_aggregate(intent)

        raise ValueError(f"Unsupported action: {action}")

    # -------------------------
    # Builders
    # -------------------------

    def _build_select(self, intent: dict) -> str:
        table = intent["table"]
        limit = intent.get("limit")

        if not table:
            raise ValueError("SELECT intent requires a table")

        sql = f"SELECT * FROM {table}"

        if limit:
            sql += f" LIMIT {limit}"

        return sql + ";"

    def _build_count(self, intent: dict) -> str:
        table = intent["table"]

        if not table:
            raise ValueError("COUNT intent requires a table")

        return f"SELECT COUNT(*) FROM {table};"

    def _build_aggregate(self, intent: dict) -> str:
        table = intent["table"]
        metric = intent["metric"]
        group_by = intent.get("group_by")

        if not table or not metric:
            raise ValueError("AGGREGATE intent requires table and metric")

        metric_sql = metric.upper()

        if group_by:
            return (
                f"SELECT {group_by}, {metric_sql}(*) "
                f"FROM {table} "
                f"GROUP BY {group_by};"
            )

        return f"SELECT {metric_sql}(*) FROM {table};"
