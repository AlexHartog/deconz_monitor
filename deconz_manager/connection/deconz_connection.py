import logging

from . import db

logger = logging.getLogger("deconz_manager.db.deconz_connection")


def get_deconz_connection_data(conn):
    connection_data = db.execute_query(conn, "SELECT * FROM deconz_connection")
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
            """
                DELETE FROM deconz_connection;
                INSERT INTO deconz_connection(ip_address, port, api_key) VALUES (%s, %s, %s)
            """,
            (ip, port, api_key),
        )


def update_deconz_connection_data(conn, ip=None, port=None, api_key=None):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM deconz_connection")
        if len(cursor.fetchall()) == 0:
            logger.warning("No deconz connection data to update")
            raise db.NoResultFound("No deconz connection data to update")

        cursor.execute(
            """UPDATE deconz_connection SET ip_address = coalesce(%s, ip_address),
            port = coalesce(%s, port), api_key = coalesce(%s, api_key)""",
            (ip, port, api_key),
        )
