import pandas as pd
from src.db.sqlite_manager import get_connection

class SQLExecutor:

    def clean_sql(self, sql):
        sql = sql.strip()
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.rstrip(";")

        return sql

    def run_query(self, sql):
        sql = self.clean_sql(sql)

        try:
            conn = get_connection()
            df = pd.read_sql_query(sql, conn)
            conn.close()

            return df

        except Exception as e:
            raise RuntimeError(f"SQL execution error: {str(e)}")