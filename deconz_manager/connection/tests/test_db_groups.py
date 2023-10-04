import datetime
import json
import logging
import os
from pathlib import Path

import pytest

import deconz_manager.connection.groups as db_groups
import deconz_manager.connection.lights as db_lights

logger = logging.getLogger("deconz_manager.tests.db_groups")

EXPECTED_GROUPS_DATA = [
    {
        "group_id": "1",
        "light_id": "2",
    },
    {
        "group_id": "1",
        "light_id": "1",
    },
    {
        "group_id": "2",
        "light_id": "2",
    },
]


def assert_groups_data(groups, expected_groups_original):
    """Compare lights data with expected data."""
    expected_groups = expected_groups_original.copy()

    assert len(groups) == len(expected_groups)

    expected_groups.sort(key=lambda light: (light["group_id"], light["light_id"]))
    groups.sort(key=lambda group: (group["group_id"], group["light_id"]))

    count = 0
    for group, expected in zip(groups, expected_groups):
        for key, value in expected.items():
            assert group[key] == value, f"{key}[{count}]: {group[key]} != {value}"

        count += 1


def test_save_groups_inserts_correct_data(conn, groups_data):
    """Test if save_groups inserts correct data."""
    db_groups.save_groups(conn, groups_data)

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM deconz_group")
        groups = cursor.fetchall()

    assert len(groups) == len(groups_data)
    assert groups[0]["id"] == next(iter(groups_data))
    assert groups[1]["group_name"] == groups_data[groups[1]["id"]]["name"]
    assert groups[1]["etag"] == groups_data[groups[1]["id"]]["etag"]


@pytest.mark.parametrize("json_data", ["groups_different.json"], indirect=True)
def test_save_groups_overwrites_correct_data(conn, groups_data, json_data):
    """Check if save_groups overwrites correct data and removes
    data that is not part of the data anymore."""
    db_groups.save_groups(conn, groups_data)
    db_groups.save_groups(conn, json_data)

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM deconz_group")
        groups = cursor.fetchall()

    key_iterator = iter(json_data)

    assert len(groups) == len(json_data)
    assert groups[0]["id"] == next(key_iterator)
    assert groups[0]["group_name"] == json_data[groups[0]["id"]]["name"]
    assert groups[1]["id"] == next(key_iterator)
    assert groups[1]["group_name"] == json_data[groups[1]["id"]]["name"]


def test_save_group_lights_inserts_correct_data(conn, lights_data, groups_data):
    """Test if save_group_lights inserts correct data."""
    db_lights.save_lights(conn, lights_data)
    db_groups.save_groups(conn, groups_data)

    db_groups.save_group_lights(conn, groups_data)

    groups = db_groups.get_groups(conn)

    assert_groups_data(groups, EXPECTED_GROUPS_DATA)


@pytest.mark.parametrize("json_data", ["groups_different.json"], indirect=True)
def test_save_group_overwrites_correct_data(conn, lights_data, groups_data, json_data):
    """Test if save_group_lights correctly overwrites data."""
    db_lights.save_lights(conn, lights_data)
    db_groups.save_groups(conn, groups_data)

    db_groups.save_group_lights(conn, groups_data)

    db_groups.save_groups(conn, json_data)
    db_groups.save_group_lights(conn, json_data)

    groups = db_groups.get_groups(conn)

    assert len(groups) == 3
    assert groups[2]["light_id"] == json_data[groups[2]["group_id"]]["lights"][0]


@pytest.mark.parametrize(
    "json_data", ["groups_non_existing_lights.json"], indirect=True
)
def test_save_group_lights_non_existing_light(conn, lights_data, json_data, caplog):
    """Test if save_group_lights inserts correct data."""
    db_lights.save_lights(conn, lights_data)
    db_groups.save_groups(conn, json_data)

    db_groups.save_group_lights(conn, json_data)

    groups = db_groups.get_groups(conn)

    assert len(groups) == 2
    assert any(
        record.levelname == "WARNING"
        and "Non existing group lights combinations:" in record.message
        for record in caplog.records
    ), "No warning message found for incorrect group light combination."
