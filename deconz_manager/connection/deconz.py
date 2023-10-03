import json
import logging

import requests

from . import db, groups, lights

logger = logging.getLogger("deconz_manager.deconz")


def get_connection_url(conn, type=None):
    # TODO: Split up this long function
    print("Start with db_conn ", conn)
    connection_data = db.get_deconz_connection_data(conn=conn)
    logger.info(f"Connection data is {connection_data}")

    if not connection_data:
        ip = "192.168.1.32"
        port = "40850"

        # Need to create connection data
        db.create_deconz_connection_data(ip, port)
        connection_data = db.get_deconz_connection_data()

        if not connection_data:
            logger.error("No connection data found and unable to create one.")
            return

    # Check if we have IP, Port and API Key
    if not connection_data["ip_address"] or not connection_data["port"]:
        logger.error("We have no ip address or port set. Can't handle this.")
        return

    if not connection_data["api_key"]:
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

        logger.info(f"Result is {api_result.json()}")
        api_key = api_result.json()[0]["success"]["username"]

        db.update_deconz_connection_data(api_key=api_key)

        connection_data = db.get_deconz_connection_data()

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
    url = get_connection_url(conn, type="lights")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(
            f"Error retrieving lights: {response.status_code} - {response.text}"
        )
        return

    lights.save_lights(conn, response.json())


def get_groups(conn):
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
    get_lights(conn)
    get_groups(conn)


def update_all_data(conn):
    get_all_data(conn)
    logger.info("Updating all data")
    lights.make_snapshot(conn)
