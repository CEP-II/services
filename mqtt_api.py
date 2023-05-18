import logging
import time
import json
import paho.mqtt.client as mqtt
import requests


# MQTT broker settings
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC = "database"

# API endpoint
API_ENDPOINT = "http://analogskilte.dk:3000/timestamps"
API_ACCIDENT_ENDPOINT = "http://analogskilte.dk:3000/accident"

# Logging setup
LOG_FILE = "mqtt_api.log"
logging.basicConfig(filename=LOG_FILE,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# MQTT client initialization
client = mqtt.Client()

# Define callback function to handle incoming MQTT messages
def on_message(client, userdata, message):
    # Decode message payload and send to API
    payload = message.payload.decode('utf-8')
    print(payload)
    try:
        payload = json.loads(payload)
        print(payload)
    except json.JSONDecodeError:
        print("failed to decode message")
    if "alarmTime" in payload:
        response = requests.post(API_ACCIDENT_ENDPOINT, json=payload,timeout=10)
    else:
        response = requests.post(API_ENDPOINT, json=payload,timeout=10)
#   print({"message"}: payload)
    logging.info("Message sent to API: %s", response.status_code)

# Define callback function to handle MQTT connection events
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker.")
        client.subscribe(TOPIC)
    else:
        logging.error("Connection to MQTT broker failed with error code %s.", rc)

# Set callback functions for incoming messages and connection events
client.on_message = on_message
client.on_connect = on_connect

# Start MQTT loop to listen for incoming messages
while True:
    try:
        # Connect to MQTT broker
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        logging.info("Connecting to MQTT broker...")
        client.loop_forever()

    except KeyboardInterrupt:
        logging.info("Stopping MQTT client.")
        client.disconnect()
        break

    except ConnectionError as e:
        logging.error("MQTT client error: %s.", e)
        logging.info("Retrying connection in 60 seconds...")
        time.sleep(60)
        continue
