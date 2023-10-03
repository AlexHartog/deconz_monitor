import logging

from psycopg2.extras import execute_values

from . import db

logger = logging.getLogger("deconz_manager.db.groups")


def save_groups(conn, groups_data):
    group_fields = {
        "etag": "etag",
        "group_name": "name",
    }

    tuple_data = []
    for id, group in groups_data.items():
        tuple_data.append(
            (id,)
            + tuple(
                db.extract_fields(group, field, default=None)
                for field in group_fields.values()
            )
        )

    columns = "id, " + ", ".join(group_fields.keys())

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            f"INSERT INTO deconz_group "
            f"({columns}) VALUES %s"
            f'ON CONFLICT ON CONSTRAINT "deconz_group_pkey" DO NOTHING',
            tuple_data,
        )


def save_group_lights(conn, groups_data):
    group_lights = []
    for group_id, data in groups_data.items():
        lights = data["lights"]
        group_combinations = [(group_id, light) for light in lights]
        group_lights.extend(group_combinations)

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            """INSERT INTO group_light (group_id, light_id) VALUES %s
            ON CONFLICT ON CONSTRAINT "group_light_pkey" DO NOTHING""",
            group_lights,
        )


def get_groups(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM groups")
        return cursor.fetchall()
