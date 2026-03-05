import sqlite3
import pandas as pd

class SQLExecutor:
    def __init__(self, db_path="data/companies.db"):

        self.conn = sqlite3.connect(db_path)

    def run_query(self, sql):

        df = pd.read_sql_query(sql, self.conn)

        return df