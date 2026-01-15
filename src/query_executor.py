import psycopg2

class QueryExecutor:
    def __init__(self, connection_params: dict):
        self.connection_params = connection_params

    def execute(self, sql: str):
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)

                # SELECT
                if cursor.description is not None:
                    return cursor.fetchall()

                # NON-SELECT
                conn.commit()
                return None
