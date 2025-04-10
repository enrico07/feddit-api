import os
from datetime import datetime

import asyncpg

DATABASE_URL = os.getenv("DATABASE_URI")


class PostgreClient:
    """
    A client for interacting with a PostgreSQL database. This class provides methods to connect to the
    database, query subfeddit IDs, and retrieve comments from the database with filtering options.
    """

    def __init__(self):
        """
        Initializes the PostgreClient instance to none.
        """
        self.pool = None

    async def connect_to_db(self):
        """
        Initializes the asyncpg connection pool.
        """
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def get_subfeddit_id(self, subfeddit_name: str) -> int:
        """
        Fetches the ID of the subfeddit from the database based on its name.

        Args:
            subfeddit_name (str): The name of the subfeddit whose ID is to be fetched.

        Returns:
            int: The ID of the subfeddit.

        Raises:
            ValueError: If no subfeddit is found with the given name.
        """
        query = "SELECT id FROM subfeddit WHERE title = $1;"

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, subfeddit_name)
            if row:
                return row["id"]
            else:
                raise ValueError(f"Subfeddit '{subfeddit_name}' not found.")

    async def get_comments(
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
        query = f"SELECT id, text FROM comment WHERE subfeddit_id = $1"
        params = [subfeddit_id]

        # If a from_date is provided, add it to the query to filter comments created after the specified date
        if from_date:
            start_date = datetime.strptime(from_date, "%d-%m-%Y")
            start_unix_timestamp = int(start_date.timestamp())

            query += " AND created_at >= $2"
            params.append(start_unix_timestamp)

        # If a to_date is provided, add it to the query to filter comments created before the specified date
        if to_date:
            end_date = datetime.strptime(to_date, "%d-%m-%Y")
            end_unix_timestamp = int(end_date.timestamp())

            query += f" AND created_at <= ${len(params)+1}"
            params.append(end_unix_timestamp)

        # Limit the number of comments retrieved based on n_comments
        query += f" ORDER BY created_at DESC LIMIT ${len(params)+1};"
        params.append(n_comments)

        # Executing the query and fetching all results
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
