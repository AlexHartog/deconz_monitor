import logging
import requests
import json

from . import db, lights, groups

logger = logging.getLogger("deconz_manager.deconz")


def get_connection_url(type=None):
    connection_data = db.get_deconz_connection_data()
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
                f"Error requesting API key: {api_result.status_code} - {api_result.text}"
            )
            return

        logger.info(f"Result is {api_result.json()}")
        api_key = api_result.json()[0]["success"]["username"]

        db.update_deconz_connection_data(api_key=api_key)

        connection_data = db.get_deconz_connection_data()

    base_url = f"http://{connection_data['ip_address']}:{connection_data['port']}/api/{connection_data['api_key']}"

    if type == "lights":
        return f"{base_url}/lights"
    elif type == "groups":
        return f"{base_url}/groups"
    elif type is None:
        return base_url


def get_lights():
    url = get_connection_url(type="lights")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(
            f"Error retrieving lights: {response.status_code} - {response.text}"
        )
        return

    lights.save_lights(response.json())


def get_groups():
    url = get_connection_url(type="groups")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(
            f"Error retrieving groups: {response.status_code} - {response.text}"
        )
        return

    groups_data = response.json()

    groups.save_groups(groups_data)
    groups.save_group_lights(groups_data)


def get_all_data():
    get_lights()
    get_groups()


def update_all_data():
    get_all_data()
    logger.info(f"Updating all data")
    lights.store_state()
    # Now we need to save history
