import logging

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

logger = logging.getLogger("deconz_manager.db")


def get_db_connection():
    conn = psycopg2.connect(
        host="192.168.1.102",
        database="deconz_manager_dev",
        user="deconz_manager",
        password="deconzm",
    )
    return conn


def execute_query(query):
    logger.info("Executing query: " + query)
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

    # mycursor.execute(
    #     """INSERT INTO products
    #                     (city_id, product_id, quantity, price)
    #                     VALUES (%s, %s, %s, %s)""",
    #     (city_id, product_id, quantity, price),
    # )
    #
    # result = execute_query(
    #     f"INSERT INTO connection(ip_address, port, api_key) VALUES ({ip}, {port}, {api_key})"
    #     f'on conflict on constraint "connection_pkey" '
    #     f"do update set ip_address='{ip}', port='{port}', api_key='{api_key}'"
    # )
    # logger.info(f"Result: {result}")


def update_deconz_connection_data(ip=None, port=None, api_key=None):
    # update_values = {
    #     "ip_address": ip,
    #     "port": port,
    #     "api_key": api_key,
    # }
    #
    # columns_to_update = [
    #     f"{column} = '{value}'"
    #     for column, value in update_values.items()
    #     if value is not None
    # ]
    #
    # if len(columns_to_update) == 0:
    #     logger.warning("No columns to update.")
    #     return

    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"UPDATE connection SET ip_address = coalesce(%s, ip_address), "
                f"port = coalesce(%s, port), api_key = coalesce(%s, api_key)"(
                    ip, port, api_key
                ),
            )
            # logger.info(f"Result: {result}")


def extract_fields(data, field_path, default=None):
    keys = field_path.split(".")
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data
