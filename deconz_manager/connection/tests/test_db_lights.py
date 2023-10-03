import logging
import json
import os
from pathlib import Path
import datetime

import pytest
from psycopg2.extras import execute_values

import deconz_manager.connection.lights as db_lights


logger = logging.getLogger("deconz_manager.tests.db_lights")

EXPECTED_LIGHTS_DATA = [
    {
        "id": "1",
        "etag": "35f4a238fd36ddd540612c8fa437f06e",
        "state_on": None,
        "last_seen": datetime.datetime(
            2023, 10, 3, 8, 36, tzinfo=datetime.timezone.utc
        ),
        "unique_id": "00:21:2e:ff:ff:07:0c:7d-01",
        "has_color": False,
        "last_announced": None,
    },
    {
        "id": "2",
        "etag": "e63955f0aae7fa44c635b17aa1479abd",
        "state_on": True,
        "last_seen": datetime.datetime(
            2023, 10, 3, 9, 19, tzinfo=datetime.timezone.utc
        ),
        "unique_id": "00:17:88:01:04:dd:bc:c2-0b",
        "has_color": True,
        "last_announced": datetime.datetime(
            2023, 9, 21, 15, 44, 48, tzinfo=datetime.timezone.utc
        ),
    },
]


@pytest.fixture()
def lights_data():
    """Load lights data from json file."""
    json_location = Path(__file__).parent / "data"

    return read_json_file(json_location, "lights.json")


def assert_lights_data(
    lights,
    expected_lights_original,
    field_to_ignore=[],
    order_key=None,
    key_mappings=None,
):
    """Compare lights data with expected data."""
    expected_lights = expected_lights_original.copy()

    assert len(lights) == len(expected_lights)

    if order_key:
        expected_lights.sort(key=lambda light: light[order_key])
        if key_mappings and order_key in key_mappings:
            order_key = key_mappings[order_key]
        lights.sort(key=lambda light: light[order_key])

    count = 0
    for light, expected in zip(lights, expected_lights):
        for key, value in expected.items():
            if key_mappings and key in key_mappings:
                key = key_mappings[key]
            if key not in field_to_ignore:
                assert light[key] == value, f"{key}[{count}]: {light[key]} != {value}"

        count += 1


def read_json_file(json_location, file_name):
    """Read a json file with specified file name and json location."""
    file_path = os.path.join(json_location, file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error - {e}")
        raise


def test_save_lights_inserts_correct_data(conn, lights_data):
    """Test if save_lights inserts correct data."""
    db_lights.save_lights(conn, lights_data)

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM light ORDER BY id")
        lights = cursor.fetchall()

    assert_lights_data(lights, EXPECTED_LIGHTS_DATA, order_key="unique_id")


def test_get_lights_correct_data(conn, lights_data):
    """Test if get_lights returns correct data."""
    db_lights.save_lights(conn, lights_data)

    lights = db_lights.get_lights(conn)

    assert_lights_data(
        lights,
        EXPECTED_LIGHTS_DATA,
        field_to_ignore=["id", "etag", "has_color"],
        order_key="unique_id",
    )


def test_make_snapshot_correct_data(conn, lights_data):
    """Test if make_snapshot creates correct data."""
    db_lights.save_lights(conn, lights_data)

    db_lights.make_snapshot(conn)

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM light_history")
        light_history = cursor.fetchall()

    assert_lights_data(
        light_history,
        EXPECTED_LIGHTS_DATA,
        field_to_ignore=[
            "id",
            "etag",
            "last_seen",
            "last_announced",
            "has_color",
        ],
        order_key="unique_id",
        key_mappings={"unique_id": "light_id"},
    )


def test_make_snapshot_id_updated(conn, lights_data):
    """Test if make_snapshot updates id."""
    db_lights.save_lights(conn, lights_data)
    db_lights.make_snapshot(conn)
    db_lights.make_snapshot(conn)

    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT distinct snapshot_id FROM light_history ORDER BY snapshot_id"
        )
        snapshot_ids = cursor.fetchall()

    assert len(snapshot_ids) == 2
    assert snapshot_ids[0]["snapshot_id"] == 1
    assert snapshot_ids[1]["snapshot_id"] == 2


def test_get_snapshot_correct_data(conn, lights_data):
    """Insert a snapshot and check if get snapshot gets the correct data."""
    db_lights.save_lights(conn, lights_data)
    db_lights.make_snapshot(conn)

    snapshot = db_lights.get_snapshot(conn, 1)

    assert_lights_data(
        snapshot,
        EXPECTED_LIGHTS_DATA[1:],
        field_to_ignore=[
            "id",
            "etag",
            "last_seen",
            "last_announced",
            "has_color",
        ],
        order_key="unique_id",
    )


def test_get_history_details_correct_data(conn, lights_data):
    """Insert a snapshot and check if get history details gets the correct data."""
    db_lights.save_lights(conn, lights_data)
    db_lights.make_snapshot(conn)

    with conn.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM light_history "
            f"WHERE light_id = '{EXPECTED_LIGHTS_DATA[1]['unique_id']}'"
        )
        id = cursor.fetchone()["id"]

    history_details = db_lights.get_history_details(conn, id)

    assert_lights_data(
        history_details,
        EXPECTED_LIGHTS_DATA[1:],
        field_to_ignore=[
            "id",
            "etag",
            "last_seen",
            "last_announced",
            "has_color",
        ],
        order_key="unique_id",
    )


def test_get_history_count_correct_data(conn, lights_data):
    """Insert a snapshot and check if get history count gets the correct data."""
    db_lights.save_lights(conn, lights_data)
    db_lights.make_snapshot(conn)

    history_count = db_lights.get_history_count(conn)[0]

    assert history_count["snapshot_id"] == 1
    assert history_count["count"] == 2
    assert history_count["on_count"] == 1


def test_get_day_averages_correct_data(conn, lights_data):
    """Insert light history and check if get day averages gets the correct data."""
    datetime_to_use = datetime.datetime(
        2023, 10, 3, 8, 36, tzinfo=datetime.timezone.utc
    )
    data_to_insert = [
        (datetime_to_use, "True", 1),
        (datetime_to_use, "False", 1),
        (datetime_to_use, "True", 1),
        (datetime_to_use, "False", 1),
        (datetime_to_use, "True", 2),
        (datetime_to_use, "True", 2),
        (datetime_to_use, "False", 2),
        (datetime_to_use, "True", 2),
        (datetime_to_use, "True", 3),
        (datetime_to_use, "False", 3),
        (datetime_to_use, "True", 3),
        (datetime_to_use, "True", 3),
    ]

    with conn.cursor() as cursor:
        execute_values(
            cursor,
            f"INSERT INTO light_history " f"(at_time, state_on, snapshot_id) VALUES %s",
            data_to_insert,
        )

        cursor.execute(f"SELECT * FROM light_history")

    day_averages = db_lights.get_day_averages(conn)

    assert day_averages[0]["avg_light_on"] == 2
