import logging

logger = logging.getLogger("deconz_manager.db")


class NoResultFound(Exception):
    """An exception raised when no result is found."""

    pass


def execute_query(conn, query):
    """Execute a query and return the results if available."""
    with conn.cursor() as cursor:
        cursor.execute(query)
        if cursor.description is None:
            return
        return [dict(row) for row in cursor.fetchall()]


def extract_fields(data, field_path, default=None):
    """This function extracts a field from a nested dictionary. The key can be multiple
    levels deep by splitting the path with a dot."""
    keys = field_path.split(".")
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data
