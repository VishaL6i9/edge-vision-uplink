import paho.mqtt.client as paho_mqtt
import time
import json
import random
import logging
import pytz
from datetime import datetime

broker_address="localhost"
broker_port=1883
telem_topic="robots/telemetry"

# Configure logging for India Standard Time (IST) in mock_bot
kolkata_timezone = pytz.timezone('Asia/Kolkata')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Callback function on connection
def on_connect(client, userdata, flags, rc):
    logger.info(f"Mock Robot MQTT Connected with result code {rc}")

# Create MQTT client
client = paho_mqtt.Client()
client.on_connect = on_connect
client.connect(broker_address, broker_port, 60)

client.loop_start() # Start the loop in a background thread

logger.info("Mock Robot: Starting telemetry simulation...")

robot_id = "robot_" + str(random.randint(1000, 9999))

x_pos = random.uniform(0, 100)
y_pos = random.uniform(0, 100)
battery_voltage = random.uniform(20, 28)
status = random.choice(["Online", "Moving", "Idle"])

try:
    while True:
        x_pos += random.uniform(-1, 1)
        y_pos += random.uniform(-1, 1)
        battery_voltage += random.uniform(-0.1, 0.1)

        # Keep values within reasonable bounds
        x_pos = max(0, min(x_pos, 100))
        y_pos = max(0, min(y_pos, 100))
        battery_voltage = max(18, min(battery_voltage, 28))

        # Get current time in Kolkata timezone
        current_time_ist = datetime.now(kolkata_timezone)

        telemetry_data = {
            "robot_id": robot_id,
            "x": round(x_pos, 2),
            "y": round(y_pos, 2),
            "battery": round(battery_voltage, 2),
            "status": status,
            "timestamp": current_time_ist.isoformat() # ISO format includes timezone offset
        }
        client.publish(telem_topic, json.dumps(telemetry_data))
        logger.info(f"Mock Robot {robot_id}: Published {telemetry_data}")
        time.sleep(random.uniform(1, 3)) # Publish every 1-3 seconds

except KeyboardInterrupt:
    logger.info("Mock Robot: Telemetry simulation stopped.")
    client.loop_stop()
    client.disconnect()