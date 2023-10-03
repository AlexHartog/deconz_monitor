import logging
import json
import os
from pathlib import Path
import datetime

import pytest

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
        cursor.execute("SELECT * FROM light")
        lights = cursor.fetchall()

    assert_lights_data(lights, EXPECTED_LIGHTS_DATA)


def assert_lights_data(lights, expected_lights):
    """Compare lights data with expected data."""
    assert len(lights) == len(expected_lights)

    for light, expected in zip(lights, expected_lights):
        for key, value in expected.items():
            assert light[key] == value
