import logging

from psycopg2.extras import RealDictCursor, execute_values

from . import db

logger = logging.getLogger("deconz_manager.db_lights")


def save_lights(conn, lights_data):
    """Save all lights data. Delete lights that are not part of data
    and update existing ones."""
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
    lights_ids = []
    for id, light in lights_data.items():
        tuple_data.append(
            (id,)
            + tuple(
                db.extract_fields(light, field, default=None)
                for field in light_fields.values()
            )
        )
        lights_ids.append(light["uniqueid"])

    columns = "id, " + ", ".join(light_fields.keys())

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM light WHERE unique_id NOT IN %s", (tuple(lights_ids),)
        )

        execute_values(
            cursor,
            f"INSERT INTO light "
            f"({columns}) VALUES %s"
            f"ON CONFLICT (unique_id) DO UPDATE "
            f'SET ({", ".join(light_fields.keys())}) = '
            f'({", ".join("EXCLUDED." + col for col in light_fields.keys())})',
            tuple_data,
        )


def get_lights(conn):
    """Get all lights."""
    lights_query = """
                SELECT *
                FROM group_light_v
            """
    return db.execute_query(conn, lights_query)


def get_history_details(conn, id: int):
    """Get details for a specific history record."""
    history_details_query = f"""
                SELECT *
                FROM light_history_v
                WHERE id={id}
            """
    return db.execute_query(conn, history_details_query)


def make_snapshot(conn):
    """Create a snapshot by saving current state."""
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
            INSERT INTO light_history
            (light_id, state_brightness, state_on, state_reachable, snapshot_id)
            SELECT unique_id, state_brightness, state_on, state_reachable, {snapshot}
            FROM light
        """
        )


def get_snapshot(conn, snapshot_id: str):
    """Get a snapshot with a specific id."""
    snapshot_query = f"""
                SELECT distinct on (light_name) *
                FROM light_history_v
                WHERE snapshot_id='{snapshot_id}' AND state_on IS NOT NULL
                AND light_name IS NOT NULL
            """
    return db.execute_query(conn, snapshot_query)


def get_history_count(conn, start_time=None, end_time=None, limit=None):
    """Get a count of lights on historically."""
    time_filter = ""
    if start_time:
        time_filter += f" AND at_time >= '{start_time}'"
    if end_time:
        time_filter += f" AND at_time <= '{end_time}'"

    history_count_query = f"""
                SELECT snapshot_id, at_time, count(*),
                sum(case when state_on then 1 else 0 end ) as on_count
                FROM light_history
                WHERE state_reachable {time_filter}
                GROUP BY at_time, snapshot_id
                ORDER BY at_time desc, snapshot_id
                { 'limit ' + str(limit) if limit else ''}
            """
    return db.execute_query(conn, history_count_query)


def get_day_averages(conn):
    """Calculate daily average lights on."""
    day_average_query = """
          SELECT
            CAST(at_time AS DATE) as date,
            SUM(CASE WHEN state_on THEN 1 ELSE 0 END) /
            COUNT(DISTINCT snapshot_id) AS avg_light_on
          FROM
          light_history
          GROUP BY CAST(at_time AS date)
    """
    return db.execute_query(conn, day_average_query)
