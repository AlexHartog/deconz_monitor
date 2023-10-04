import logging

import psycopg2.errors
import psycopg2.extras
import pytest

from deconz_manager.connection import db, deconz_connection

logger = logging.getLogger("deconz_manager.tests.deconz_connection")


def test_create_deconz_connection_data(conn):
    """Create a deconz connection and check values."""
    test_api_key = "api"
    test_port = "8000"
    test_ip = "test_ip"

    deconz_connection.create_deconz_connection_data(
        conn, api_key=test_api_key, port=test_port, ip=test_ip
    )
    results = db.execute_query(conn, "SELECT * FROM deconz_connection")

    assert results[0]["api_key"] == test_api_key
    assert results[0]["ip_address"] == test_ip
    assert results[0]["port"] == test_port


def test_create_double_connection_data(conn):
    """Create a deconz connection twice and make sure we only have one record."""
    deconz_connection.create_deconz_connection_data(conn, api_key="test")
    deconz_connection.create_deconz_connection_data(conn, api_key="test2")

    results = db.execute_query(conn, "SELECT * FROM deconz_connection")

    assert len(results) == 1


def test_get_connection_data(conn):
    """Check if deconz get data works."""
    test_api_key = "api_test"
    deconz_connection.create_deconz_connection_data(conn, api_key=test_api_key)

    connection_data = deconz_connection.get_deconz_connection_data(conn)

    assert connection_data["api_key"] == test_api_key


def test_get_connect_data_unavailable(conn):
    """Check if get deconz connection data returns None if not available."""
    connection_data = deconz_connection.get_deconz_connection_data(conn)

    assert connection_data is None


def test_get_connection_data_multiple(conn):
    deconz_connection.create_deconz_connection_data(
        conn, api_key="test", port="1000", ip="test"
    )

    with conn.cursor() as cursor:
        with pytest.raises(psycopg2.errors.UniqueViolation):
            cursor.execute(
                """
                INSERT INTO
                deconz_connection (api_key, port, ip_address)
                VALUES ('test2', '1001', 'test2')
                """
            )


def test_update_connection_data(conn):
    deconz_connection.create_deconz_connection_data(
        conn, api_key="test", port="1000", ip="test"
    )

    api_key = "new_api_key"
    port = "3000"
    ip = "new_ip"
    deconz_connection.update_deconz_connection_data(
        conn, api_key=api_key, port=port, ip=ip
    )

    result = db.execute_query(conn, "SELECT * FROM deconz_connection")[0]

    assert result["api_key"] == api_key
    assert result["port"] == port
    assert result["ip_address"] == ip


def test_update_connection_data_unavailable(conn):
    with pytest.raises(db.NoResultFound):
        deconz_connection.update_deconz_connection_data(conn, api_key="test")
