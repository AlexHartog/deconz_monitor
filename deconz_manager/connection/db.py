import logging

logger = logging.getLogger("deconz_manager.db")


class NoResultFound(Exception):
    pass


def execute_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        if cursor.description:
            return cursor.fetchall()
        else:
            return None


def extract_fields(data, field_path, default=None):
    keys = field_path.split(".")
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data
