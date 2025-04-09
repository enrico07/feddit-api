import os
from datetime import datetime

import psycopg
from psycopg import Connection, Cursor
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URI")


class PostgreClient:
    """
    A client for interacting with a PostgreSQL database. This class provides methods to connect to the
    database, query subfeddit IDs, and retrieve comments from the database with filtering options.
    """

    def __init__(self):
        """
        Initializes the PostgreClient instance by connecting to the database and setting up the cursor.
        """
        self.cursor, self.conn = self._connect_to_db()

    @staticmethod
    def _connect_to_db() -> tuple[Cursor, Connection]:
        """
        Establishes a connection to the PostgreSQL database and creates a cursor for executing queries.

        Returns:
            tuple: A tuple containing the cursor and connection objects.
        """
        # Connecting to the database using psycopg and returning a cursor and connection object
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor(row_factory=dict_row)

        return cursor, conn

    def get_subfeddit_id(self, subfeddit_name: str) -> int:
        """
        Fetches the ID of the subfeddit from the database based on its name.

        Args:
            subfeddit_name (str): The name of the subfeddit whose ID is to be fetched.

        Returns:
            int: The ID of the subfeddit.

        Raises:
            ValueError: If no subfeddit is found with the given name.
        """
        query = "SELECT id FROM subfeddit WHERE title = %s;"

        try:
            # Executing the query and fetching the result
            self.cursor.execute(query, (subfeddit_name,))
            result = self.cursor.fetchone()
        except Exception as e:
            self.cursor.execute("ROLLBACK")
            raise e

        # If the subfeddit exists, return its ID
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
        """
        Retrieves comments from the database for a given subfeddit, with optional filtering by date range and number.

        Args:
            subfeddit_id (str): The ID of the subfeddit for which comments are to be fetched.
            from_date (str, optional): The start date for filtering comments. Defaults to None.
            to_date (str, optional): The end date for filtering comments. Defaults to None.
            n_comments (int, optional): The maximum number of comments to retrieve. Defaults to 25.

        Returns:
            list: A list of comments, each represented as a dictionary containing the comment data.
        """
        query = f"SELECT id, text FROM comment WHERE subfeddit_id = %s"
        params = (subfeddit_id,)

        # If a from_date is provided, add it to the query to filter comments created after the specified date
        if from_date:
            start_date = datetime.strptime(from_date, "%d-%m-%Y")
            start_unix_timestamp = int(start_date.timestamp())

            query += " AND created_at >= %s"
            params += (start_unix_timestamp,)

        # If a to_date is provided, add it to the query to filter comments created before the specified date
        if to_date:
            end_date = datetime.strptime(to_date, "%d-%m-%Y")
            end_unix_timestamp = int(end_date.timestamp())

            query += " AND created_at <= %s"
            params += (end_unix_timestamp,)

        # Limit the number of comments retrieved based on n_comments
        query += " ORDER BY created_at DESC LIMIT %s;"
        params += (n_comments,)

        try:
            # Executing the query and fetching all results
            self.cursor.execute(query, params)
            res = self.cursor.fetchall()
        except Exception as e:
            self.cursor.execute("ROLLBACK")
            raise e

        return res
