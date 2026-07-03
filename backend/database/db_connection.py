"""
db_connection.py

Handles PostgreSQL database connections.
"""

import psycopg2

from backend.database.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD
)


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


def get_connection():
    """
    Creates and returns a PostgreSQL connection.
    """

    try:

        connection = psycopg2.connect(

            host=DB_HOST,

            port=DB_PORT,

            database=DB_NAME,

            user=DB_USER,

            password=DB_PASSWORD

        )

        return connection

    except Exception as e:

        raise DatabaseConnectionError(
            f"Unable to connect to database.\n{e}"
        )
    

if __name__ == "__main__":

    try:

        conn = get_connection()

        print("Database Connected Successfully!")

        conn.close()

    except Exception as e:

        print(e)