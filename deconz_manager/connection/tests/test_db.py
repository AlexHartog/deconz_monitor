import os
import pytest
import psycopg2.extras 
from dotenv import load_dotenv

load_dotenv()

from deconz_manager.connection import db 


@pytest.fixture()
def conn():
    conn = psycopg2.connect(os.environ["TEST_DATABASE_URL"])
    conn.cursor_factory = psycopg2.extras.RealDictCursor

    try:
        yield conn
    finally:
        conn.close()


def test_create_deconz_connection_data(conn):
    test_api_key = "api"
    test_port = "8000"
    test_ip = "test_ip"

    db.create_deconz_connection_data(conn, api_key=test_api_key, port=test_port, ip=test_ip)
    results = db.execute_query(conn, "SELECT * FROM connection")

    assert results[0]["api_key"] == test_api_key
    assert results[0]["ip_address"] == test_ip
    assert results[0]["port"] == test_port


def test_create_double_connection_data(conn):
    db.create_deconz_connection_data(conn, api_key="test")
    db.create_deconz_connection_data(conn, api_key="test2")

    results = db.execute_query(conn, "SELECT * FROM connection")

    assert len(results) == 1


def test_get_connection_data(conn):
    test_api_key = "api_test"
    db.create_deconz_connection_data(conn, api_key=test_api_key)

    connection_data = db.get_deconz_connection_data(conn)
    
    assert connection_data["api_key"] == test_api_key