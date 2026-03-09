class SQLAgent:

    def __init__(self, llm_client, schema):

        self.llm = llm_client
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