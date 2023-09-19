from flask import Flask

app = Flask(__name__)


import asyncio
import json

import aiohttp
import requests
from pydeconz import DeconzSession

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

response = requests.post(f"http://{internal_ip}:{internal_port}/api", data=body)

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

@app.route("/")
def index():
    return 'Let\'s go!'

