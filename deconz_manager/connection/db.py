import logging
import os


import random

from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor, NamedTupleCursor

from dotenv import load_dotenv

logger = logging.getLogger("deconz_manager.db")

load_dotenv()

class PostgresDB:
    def __init__(self):
        self.app = None
        self.pool = None

    def init_app(self, app):
        self.app = app
        self.connect()

    def connect(self):
        #TODO 
        self.pool = SimpleConnectionPool(
            1, 20,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE")
        )
        return self.pool

    @contextmanager
    def cursor(self, cursor_factory=None):
        if self.pool is None:
            self.connect()
        con = self.pool.getconn()
        random_int = random.randint(1, 1000)
        try:
            print("Opening for ", random_int)
            yield con.cursor(cursor_factory=RealDictCursor)
            con.commit()
        finally:
            print("Closing again for ", random_int)
            self.pool.putconn(con)


def execute_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_deconz_connection_data(conn):
    connection_data = execute_query(conn, "SELECT * FROM connection")
    if len(connection_data) == 0:
        logger.info("No connection data found.")
        return
    elif len(connection_data) > 1:
        logger.error("Multiple connection data found. This should not happen.")
        return
    return connection_data[0]


def create_deconz_connection_data(conn, ip=None, port=None, api_key=None):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""
                DELETE FROM connection;
                INSERT INTO connection(ip_address, port, api_key) VALUES (%s, %s, %s)
            """,
            (ip, port, api_key),
        )


def update_deconz_connection_data(conn, ip=None, port=None, api_key=None):
    with conn.cursor() as cursor:
        cursor.execute(
            f"UPDATE connection SET ip_address = coalesce(%s, ip_address), "
            f"port = coalesce(%s, port), api_key = coalesce(%s, api_key)",
            (ip, port, api_key),
        )


def extract_fields(data, field_path, default=None):
    keys = field_path.split(".")
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data
