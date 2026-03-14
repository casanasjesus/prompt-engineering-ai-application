from pathlib import Path
from src.db.sqlite_manager import get_connection

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "database" / "data_assistant.db"

class SQLAgent:

    def __init__(self, llm_client, db_path=DB_FILE):

        self.llm = llm_client
        self.db_path = db_path

    def get_schema_from_db(self):

        conn = get_connection()
        cursor = conn.cursor()

        schema_text = ""

        # Get tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )

        tables = cursor.fetchall()

        for (table_name,) in tables:

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            col_names = [col[1] for col in columns]

            schema_text += f"{table_name}({', '.join(col_names)})\n"

        conn.close()

        return schema_text


    def generate_sql_stream(self, question):

        schema_text = self.get_schema_from_db()

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