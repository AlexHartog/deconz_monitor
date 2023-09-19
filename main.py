from pydeconz import DeconzSession
import aiohttp
import asyncio
import requests
import json

# Replace with the IP address and port of your ConBee stick
host = "192.168.1.32"
port = 40850
websocket_port = 80

response = requests.get("https://phoscon.de/discover")

if response.status_code != 200:
    raise Exception("Error: %s" % response.status_code)

response_body = response.json()

if len(response_body) != 1:
    raise Exception(f"Received {len(response_body)} responses. Expected 1.")

deconz_data = response_body[0]

internal_ip = deconz_data["internalipaddress"]
internal_port = deconz_data["internalport"]
internal_ip = "192.168.1.32"

body = json.dumps({
    "devicetype": "python_test",
})

response = requests.post(f"http://{internal_ip}:{internal_port}/api", json={"name": "PhosconGW"}, data=body)

if response.status_code != 200:
    for error_msg in response.json():
        # print("Error msg: ", error_msg)
        error = error_msg['error']
        print("Error: ", error)
    raise Exception("Error: %s" % response.status_code)

print(f"Response: {response.json()}")

if len(response.json()) != 1:
    raise Exception(f"Received {len(response.json())} responses. Expected 1.")

username = response.json()[0]["success"]["username"]

print(f"Received username: {username}")

api_body = [
    {
        "id": "00212EFFFF070C7D",
        "internalipaddress": "172.30.33.2",
        "macaddress": "00212EFFFF070C7D",
        "internalport": 40850,
        "name": "PhosconGW",
        "publicipaddress": "217.123.61.101"
    }
]


# # Initialize a session
# with aiohttp.ClientSession() as aiohttp_session:
#     session = DeconzSession(aiohttp_session, host, port)
#
# # Connect to the ConBee stick
# session.start()
#
# # Authenticate if needed (you may need to obtain an API key)
# api_key = "your_api_key"  # Replace with your API key
# session.register(api_key)
#
# # List the available sensors
# sensors = session.sensors
# print("Available Sensors:")
# for sensor in sensors:
#     print(sensor)


# async def fetch_data():
#     async with aiohttp.ClientSession() as aiohttp_session:
#         session = DeconzSession(aiohttp_session, host, port)
#         session.start(websocketport=websocket_port)
#
#         print("Session started ", session)
#
#         sensors = session.sensors
#         print("Available Sensors:")
#         for sensor in sensors:
#             print(sensor)
#
#
# async def main():
#     data = await fetch_data()
#     print(data)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

# You can now interact with the sensors and devices connected to the ConBee stick
