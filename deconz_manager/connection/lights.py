from psycopg2.extras import RealDictCursor, execute_values
import logging

from . import db

logger = logging.getLogger("deconz_manager.db_lights")


def save_lights(lights_data):
    light_fields = {
        "unique_id": "uniqueid",
        "etag": "etag",
        "has_color": "hascolor",
        "last_announced": "lastannounced",
        "last_seen": "lastseen",
        "manufacturer_name": "manufacturername",
        "model_id": "modelid",
        "light_name": "name",
        "product_id": "productid",
        "product_name": "productname",
        "sw_version": "swversion",
        "light_type": "type",
        "state_brightness": "state.bri",
        "state_on": "state.on",
        "state_reachable": "state.reachable",
    }

    tuple_data = []
    for id, light in lights_data.items():
        tuple_data.append(
            (id,)
            + tuple(
                db.extract_fields(light, field, default=None)
                for field in light_fields.values()
            )
        )

    columns = "id, " + ", ".join(light_fields.keys())

    with db.get_db_connection() as conn:
        with conn.cursor() as cursor:
            execute_values(
                cursor,
                f"INSERT INTO light "
                f"({columns}) VALUES %s"
                f"ON CONFLICT (unique_id) DO UPDATE "
                f'SET ({", ".join(light_fields.keys())}) = '
                f'({", ".join("EXCLUDED." + col for col in light_fields.keys())})',
                tuple_data,
            )


def get_lights():
    lights_query = """
                SELECT * 
                FROM group_light_v
            """
    return execute_select_query(lights_query)


def get_history_details(id: int):
    history_details_query = f"""
                SELECT * 
                FROM light_history_v
                WHERE id={id}
            """
    return execute_select_query(history_details_query)


def store_state():
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT COALESCE(max(snapshot_id), 0) AS max_snapshot
                FROM light_history
            """
            )

            max_snapshot = cursor.fetchone()["max_snapshot"]

            snapshot = max_snapshot + 1

            cursor.execute(
                f"""
                INSERT INTO light_history (light_id, state_brightness, state_on, state_reachable, snapshot_id)
                SELECT unique_id, state_brightness, state_on, state_reachable, {snapshot} FROM light
            """
            )


def get_snapshot(snapshot_id: str):
    snapshot_query = f"""
                SELECT distinct on (light_name) * 
                FROM light_history_v
                WHERE snapshot_id='{snapshot_id}' AND state_on IS NOT NULL AND light_name IS NOT NULL
            """
    return execute_select_query(snapshot_query)


def get_history_count():
    history_count_query = """
                SELECT snapshot_id, at_time, count(*), 
                sum(case when state_on then 1 else 0 end ) as on_count
                FROM light_history 
                WHERE state_reachable
                GROUP BY at_time, snapshot_id
                ORDER BY at_time desc, snapshot_id 
            """
    return execute_select_query(history_count_query)


def execute_select_query(query):
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
