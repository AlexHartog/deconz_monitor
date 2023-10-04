import json
import logging

import requests

from . import db, groups, lights, deconz_connection

logger = logging.getLogger("deconz_manager.deconz")


def get_connection_data(conn):
    """Get connection data if available and otherwise create new one."""
    connection_data = deconz_connection.get_deconz_connection_data(conn=conn)

    if not connection_data:
        # TODO: Where to store this?
        ip = "192.168.1.32"
        port = "40850"

        deconz_connection.create_deconz_connection_data(conn, ip, port)
        connection_data = deconz_connection.get_deconz_connection_data(conn)

        if not connection_data:
            logger.error("No connection data found and unable to create one.")
            return

    if not connection_data["ip_address"] or not connection_data["port"]:
        logger.error("We have no ip address or port set. Can't handle this.")
        return

    return connection_data


def valid_api_key(connection_data, conn):
    """Check if we have an API key and otherwise request one."""
    if connection_data["api_key"]:
        return connection_data["api_key"]

    logger.info("We have no api key set, requesting one now.")

    url = f"http://{connection_data['ip_address']}:{connection_data['port']}/api"
    # TODO: Save app name somewhere
    try:
        data = json.dumps(
            {
                "devicetype": "python_test",
            }
        )
        # TODO: Tell user to press button first
        logger.info(f"Requesting API key at {url}")
        api_result = requests.post(
            url,
            data=data,
        )
    except requests.exceptions.InvalidURL:
        logger.error(f"Invalid URL: {url}")
        return
    except Exception as e:
        logger.error(f"Error requesting API key: {type(e)}")
        return

    if api_result.status_code != 200:
        logger.error(
            f"""
            Error requesting API key:
            {api_result.status_code} - {api_result.text}
            """
        )
        return

    api_key = api_result.json()[0]["success"]["username"]

    deconz_connection.update_deconz_connection_data(conn, api_key=api_key)

    return api_key


def get_connection_url(conn, type=None):
    """Create a connection URL based on IP, port and API key."""
    connection_data = get_connection_data(conn)
    if not connection_data:
        return

    api_key = valid_api_key(connection_data, conn)
    if not api_key:
        return

    base_url = (
        f"http://{connection_data['ip_address']}:"
        f"{connection_data['port']}/api/"
        f"{connection_data['api_key']}"
    )

    if type == "lights":
        return f"{base_url}/lights"
    elif type == "groups":
        return f"{base_url}/groups"
    elif type is None:
        return base_url


def get_lights(conn):
    """Request lights data from deconz and save in database."""
    url = get_connection_url(conn, type="lights")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(
            f"Error retrieving lights: {response.status_code} - {response.text}"
        )
        return

    lights.save_lights(conn, response.json())


def get_groups(conn):
    """Get groups data from deconz and save in database."""
    url = get_connection_url(conn, type="groups")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(
            f"Error retrieving groups: {response.status_code} - {response.text}"
        )
        return

    groups_data = response.json()

    groups.save_groups(conn, groups_data)
    groups.save_group_lights(conn, groups_data)


def get_all_data(conn):
    """Get all data from deconz and save in database."""
    get_lights(conn)
    get_groups(conn)


def update_all_data(conn):
    """Update deconz data and make a snapshot."""
    get_all_data(conn)
    logger.info("Updating all data")
    lights.make_snapshot(conn)
