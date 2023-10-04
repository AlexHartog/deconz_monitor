import json
import logging
import os
from pathlib import Path

import psycopg2
import psycopg2.extras
import pytest
from psycopg2 import OperationalError

from deconz_manager import create_app

logger = logging.getLogger("deconz_manager.conftest")


@pytest.fixture()
def app():
    # other setup can go here

    app = create_app()
    yield app

    # clean up / reset resources here


@pytest.fixture()
def conn():
    try:
        conn = psycopg2.connect(os.environ["TEST_DATABASE_URL"])
    except OperationalError as e:
        logger.error("Unable to connect to database: %s", e)
        pytest.exit("Unable to connect to database.")

    conn.cursor_factory = psycopg2.extras.RealDictCursor

    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def lights_data():
    """Load lights data from json file."""
    json_location = Path(__file__).parent / "data"
    return read_json_file(json_location, "lights.json")


@pytest.fixture()
def groups_data():
    """Load groups data from json file."""
    json_location = Path(__file__).parent / "data"
    return read_json_file(json_location, "groups.json")


@pytest.fixture()
def json_data(request):
    """Load json file with specific file name."""
    json_location = Path(__file__).parent / "data"
    return read_json_file(json_location, request.param)


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
