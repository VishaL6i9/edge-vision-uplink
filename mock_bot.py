import paho.mqtt.client as paho_mqtt
import time
import json
import random

broker_address="localhost"
broker_port=1883
telemetry_topic="robots/telemetry"

# Callback function on connection
def on_connect(client, userdata, flags, rc):
    print(f"Mock Robot MQTT Connected with result code {rc}")

# Create MQTT client
client = paho_mqtt.Client()
client.on_connect = on_connect
client.connect(broker_address, broker_port, 60)

client.loop_start() # Start the loop in a background thread

print("Mock Robot: Starting telemetry simulation...")

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

        telemetry_data = {
            "robot_id": robot_id,
            "x": round(x_pos, 2),
            "y": round(y_pos, 2),
            "battery": round(battery_voltage, 2),
            "status": status,
            "timestamp": time.time()
        }
        client.publish(telemetry_topic, json.dumps(telemetry_data))
        print(f"Mock Robot {robot_id}: Published {telemetry_data}")
        time.sleep(random.uniform(1, 3)) # Publish every 1-3 seconds

except KeyboardInterrupt:
    print("Mock Robot: Telemetry simulation stopped.")
    client.loop_stop()
    client.disconnect()
