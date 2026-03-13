import re

def parse_sql_schema(sql):

    tables = {}

    table_matches = re.findall(
        r'create\s+table\s+(\w+)\s*\((.*?)\);?',
        sql,
        re.I | re.S
    )

    for table_name, cols_block in table_matches:

        columns = {}
        primary_keys = []
        foreign_keys = []

        lines = [line.strip() for line in cols_block.split(",")]

        for line in lines:

            parts = line.split()

            if len(parts) < 2:
                continue

            col_name = parts[0]
            col_type = parts[1]

            not_null = "NOT NULL" in line.upper()
            auto_increment = "AUTO_INCREMENT" in line.upper()
            unique = "UNIQUE" in line.upper()

            is_primary = "PRIMARY KEY" in line.upper()

            if is_primary:
                primary_keys.append(col_name)

            columns[col_name] = {
                "type": col_type,
                "not_null": not_null,
                "default": None,
                "primary_key": is_primary,
                "unique": unique,
                "auto_increment": auto_increment,
                "check": None
            }

        tables[table_name.lower()] = {
            "columns": columns,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys
        }

    return tables

class SQLAgent:

    def __init__(self, llm_client, schema):

        self.llm = llm_client

        # Detect if schema is SQL text
        if isinstance(schema, str):
            self.schema = parse_sql_schema(schema)
        else:
            self.schema = schema

    def generate_sql_stream(self, question):

        schema_text = ""

        for table, info in self.schema.items():
            cols = list(info["columns"].keys())
            schema_text += f"{table}({', '.join(cols)})\n"

        prompt = f"""
    You are a SQL expert.

    Database schema:

    {schema_text}

    User question:
    {question}

    Rules:

    - Only generate SQL
    - No explanations
    - No markdown
    - Use valid SQLite syntax
    """

        stream = self.llm.generate_stream(prompt)

        for chunk in stream:
            yield chunk