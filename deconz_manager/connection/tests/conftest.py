import logging
import os

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
