class SQLAgent:

    def __init__(self, llm_client, schema):
        self.llm = llm_client
        self.schema = schema

    def generate_sql(self, question):

        prompt = f"""
You are a SQL expert.

Database schema:
{self.schema}

User question:
{question}

RULES:
- Return ONLY the SQL query
- Do NOT explain anything
- Do NOT use markdown
- SQL must be valid

Example:

SELECT * FROM companies;

SQL:
"""

        response = self.llm.generate(prompt)

        return response.strip()