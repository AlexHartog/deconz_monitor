import logging

from psycopg2.extras import execute_values

from . import db

logger = logging.getLogger("deconz_manager.db.groups")


def save_groups(conn, groups_data):
    """Save groups in deconz_group. Delete groups that are not part
    of data and update existing ones."""
    group_fields = {
        "etag": "etag",
        "group_name": "name",
    }

    tuple_data = []
    group_ids = []
    for id, group in groups_data.items():
        tuple_data.append(
            (id,)
            + tuple(
                db.extract_fields(group, field, default=None)
                for field in group_fields.values()
            )
        )
        group_ids.append(id)

    columns = "id, " + ", ".join(group_fields.keys())

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM deconz_group WHERE id NOT IN %s",
            (tuple(group_ids),),
        )

        execute_values(
            cursor,
            f"INSERT INTO deconz_group "
            f"({columns}) VALUES %s "
            f'ON CONFLICT ON CONSTRAINT "deconz_group_pkey" DO UPDATE '
            f'SET ({", ".join(group_fields.keys())}) = '
            f'({", ".join("EXCLUDED." + col for col in group_fields.keys())})',
            tuple_data,
        )


def create_group_light_combinations(conn, groups_data):
    """Create a list of group_light tuples and exclude non existing group_light combinations."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM light")
        existing_light_ids = [light["id"] for light in cursor.fetchall()]

        cursor.execute("SELECT * FROM deconz_group")
        existing_group_ids = [group["id"] for group in cursor.fetchall()]

    group_lights = []
    non_existing_group_lights = []
    for group_id, data in groups_data.items():
        lights = data["lights"]
        for light in lights:
            if light not in existing_light_ids or group_id not in existing_group_ids:
                non_existing_group_lights.append((group_id, light))
                continue
            group_lights.append((group_id, light))

    if non_existing_group_lights:
        logger.warning(
            f"Non existing group lights combinations: {non_existing_group_lights}"
        )

    return group_lights


def save_group_lights(conn, groups_data):
    """Save group_light combinations."""
    group_lights = create_group_light_combinations(conn, groups_data)

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM group_light WHERE (group_id, light_id) NOT IN %s",
            (tuple(group_lights),),
        )

        execute_values(
            cursor,
            """INSERT INTO group_light (group_id, light_id) VALUES %s
            ON CONFLICT ON CONSTRAINT group_light_pkey DO NOTHING""",
            group_lights,
        )


def get_groups(conn):
    """Get all group lights."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM group_light")
        return cursor.fetchall()
