import logging
import os

import psycopg2
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv

logger = logging.getLogger("deconz_manager.db")

load_dotenv()


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    return conn


def execute_query(query):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_deconz_connection_data():
    connection_data = execute_query("SELECT * FROM connection")
    if len(connection_data) == 0:
        logger.info("No connection data found.")
        return
    elif len(connection_data) > 1:
        logger.error("Multiple connection data found. This should not happen.")
        return
    return connection_data[0]


def create_deconz_connection_data(ip=None, port=None, api_key=None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"INSERT INTO connection(ip_address, port, api_key) VALUES (%s, %s, %s)",
                (ip, port, api_key),
            )


def update_deconz_connection_data(ip=None, port=None, api_key=None):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
