from datetime import datetime

import psycopg
import yaml
from psycopg.rows import dict_row


class PostgreClient:
    def __init__(self):
        self.cursor, self.conn = self._connect_to_db()

    @staticmethod
    def _connect_to_db() -> None:
        with open("app/config.yaml", "r") as file:
            config = yaml.safe_load(file)
        DB_CONFIG = config.get("database", {})

        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor(row_factory=dict_row)

        return cursor, conn

    def get_subfeddit_id(self, subfeddit_name: str) -> int:
        query = "SELECT id FROM subfeddit WHERE title = %s;"

        try:
            self.cursor.execute(query, (subfeddit_name,))
            result = self.cursor.fetchone()
        except Exception as e:
            self.cursor.execute("ROLLBACK")
            raise e

        if result:
            return result["id"]
        else:
            raise ValueError(f"Subfeddit '{subfeddit_name}' not found.")

    def get_comments(
        self,
        subfeddit_id: str,
        from_date: str = None,
        to_date: str = None,
        n_comments: int = 25,
    ) -> list:
        query = f"SELECT id, text FROM comment WHERE subfeddit_id = %s"
        params = (subfeddit_id,)

        if from_date:
            start_date = datetime.strptime(from_date, "%d-%m-%Y")
            start_unix_timestamp = int(start_date.timestamp())

            query += " AND created_at >= %s"
            params += (start_unix_timestamp,)

        if to_date:
            end_date = datetime.strptime(to_date, "%d-%m-%Y")
            end_unix_timestamp = int(end_date.timestamp())

            query += " AND created_at <= %s"
            params += (end_unix_timestamp,)

        query += " ORDER BY created_at DESC LIMIT %s;"
        params += (n_comments,)

        try:
            self.cursor.execute(query, params)
            res = self.cursor.fetchall()
        except Exception as e:
            self.cursor.execute("ROLLBACK")
            raise e

        return res
