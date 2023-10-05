import os
from contextlib import contextmanager

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

load_dotenv()


class PostgresDB:
    """This class handles the connection to the postgres database."""

    def __init__(self):
        self.app = None
        self.pool = None

    def connect(self):
        """Create a connection pool using the environment variables."""
        self.pool = SimpleConnectionPool(
            1,
            20,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
        )
        return self.pool

    @contextmanager
    def cursor(self, cursor_factory=None):
        """Create a cursor using the connection pool."""
        if self.pool is None:
            self.connect()
        con = self.pool.getconn()
        try:
            yield con.cursor(cursor_factory=RealDictCursor)
            con.commit()
        finally:
            self.pool.putconn(con)


postgres_db = PostgresDB()
