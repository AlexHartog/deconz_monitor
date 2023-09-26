from psycopg2.extras import RealDictCursor, execute_values
import logging
from datetime import datetime, timedelta

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
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT * 
                FROM group_light_v
            """
            )
            return cursor.fetchall()


def get_light_history_details(id: int):
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT * 
                FROM light_history_v
                WHERE id={id}
            """
            )
            return cursor.fetchall()


def store_state():
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT COALESCE(max(snapshot), 0) AS max_snapshot
                FROM light_history
            """
            )

            max_snapshot = cursor.fetchone()["max_snapshot"]

            snapshot = max_snapshot + 1

            cursor.execute(
                f"""
                INSERT INTO light_history (light_id, state_brightness, state_on, state_reachable, snapshot)
                SELECT unique_id, state_brightness, state_on, state_reachable, {snapshot} FROM light
            """
            )


def add_snapshots():
    history_count = get_history_count()

    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            snapshot = 1
            for history in history_count:
                at_time = history["at_time"]
                # at_time_end = datetime.strptime(at_time, "%Y-%m-%d %H:%M:%S.%f%z")
                # logger.debug(f"At time: {at_time}")
                at_time_start = at_time - timedelta(seconds=1)
                at_time_end = at_time + timedelta(seconds=1)
                # logger.debug(f"At time end: {at_time_end}")
                # at_time_end = at_time[:index] + newstring + at_time[index + 1:]

                query = f"""
                    UPDATE light_history 
                    SET snapshot = {snapshot} 
                    WHERE at_time > '{at_time_start}' and at_time < '{at_time_end}'
                """
                # logger.debug(f"Query: {query}")
                cursor.execute(query)

                snapshot += 1
                # break

                # logger.debug(f"History at time - {history['at_time']}")
                #
                # if snapshot > 5:
                #     break


def get_snapshot(at_time: str):
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                f"""
                SELECT * 
                FROM light_history_v
                WHERE at_time='{at_time}'
            """
            )


def get_history_count():
    with db.get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT at_time, count(*), 
                sum(case when state_on then 1 else 0 end ) as on_count
                FROM light_history 
                GROUP BY at_time 
                ORDER BY at_time ASC
            """
            )
            return cursor.fetchall()
