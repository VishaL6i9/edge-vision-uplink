import reflex as rx
import reflex_chakra as rx_chakra

import threading
import paho.mqtt.client as paho_mqtt
import json
import asyncio
from typing import Dict, List, Any

# Import for logging timezone
import logging
import pytz
from datetime import datetime
from time import struct_time

# Configure logging for India Standard Time (IST)
kolkata_timezone = pytz.timezone('Asia/Kolkata')

def timetuple_converter(timestamp_seconds: float) -> struct_time:
    """
    Converts a timestamp (seconds since epoch) to a struct_time
    object in the Asia/Kolkata timezone.
    """
    dt_object = datetime.fromtimestamp(timestamp_seconds, tz=pytz.utc)
    kolkata_dt_object = dt_object.astimezone(kolkata_timezone)
    return kolkata_dt_object.timetuple()

logging.Formatter.converter = timetuple_converter

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')

# Ensure only one handler is added to avoid duplicate log messages
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Global event loop for rx.run_sync
main_event_loop = None

# MQTT Client Logic
def on_connect(client, userdata, flags, rc):
    logger.info(f"MQTT Connected with result code {rc}")
    client.subscribe("robots/telemetry")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if main_event_loop:
            # Safely schedule the state update on the main Reflex event loop
            # rx.run_sync is the recommended way to update state from external threads
            rx.run_sync(State.update_robot_data(payload))
        else:
            logger.warning("main_event_loop not set. State update skipped for MQTT message.")
    except Exception as e:
        logger.error(f"Error processing MQTT message: {e}")

def mqtt_thread_loop():
    client = paho_mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("mosquitto", 1883, 60)
    client.loop_forever()

# Define the main Reflex State
class State(rx.State):
    robots: Dict[str, Dict[str, Any]] = {}
    incidents: List[Dict[str, Any]] = []

    @rx.var
    def robot_locations(self) -> List[Dict[str, Any]]:
        return [
            {'x': r.get('x', 0), 'y': r.get('y', 0), 'id': robot_id}
            for robot_id, r in self.robots.items()
        ]

    _mqtt_started = False
    
    @rx.event
    async def start_mqtt_client(self):
        """Start the MQTT client in a separate thread."""
        global main_event_loop
        if self._mqtt_started:
            return
        self.__class__._mqtt_started = True
        main_event_loop = asyncio.get_running_loop()
        mqtt_thread = threading.Thread(target=mqtt_thread_loop)
        mqtt_thread.daemon = True
        mqtt_thread.start()
        logger.info("MQTT client thread started.")

    @rx.event
    async def update_robot_data(self, payload: Dict[str, Any]):
        async with self:
            robot_id = payload.get('robot_id')
            if robot_id:
                self.robots[robot_id] = payload
                logger.info(f"Updated robot {robot_id}: {payload}")
        # The return value is consumed by rx.run_sync but not directly used.
        # It's good practice for an event handler to return a value if it modifies state.
        return {"status": "success", "message": f"Robot {robot_id} updated."}

    def add_incident(self, incident_data: dict):
        self.incidents.append(incident_data)
        logger.info(f"Added incident: {incident_data}")

# UI definition
def robot_card(robot_id: str, robot_data: dict):
    return rx_chakra.card(
        rx_chakra.vstack(
            rx_chakra.heading(f"Robot ID: {robot_id}", size="lg"),
            rx_chakra.text(f"X: {robot_data.get('x', 'N/A')}, Y: {robot_data.get('y', 'N/A')}"),
            rx_chakra.hstack(
                rx_chakra.text(f"Battery: {robot_data.get('battery', 'N/A')}V"),
                rx_chakra.progress(value=robot_data.get('battery', 0), max=100, width="100px"),
            ),
            rx_chakra.text(f"Status: {robot_data.get('status', 'N/A')}"),
            width="100%",
            align_items="flex-start",
        ),
        width="100%",
    )

def index():
    return rx_chakra.center(
        rx_chakra.vstack(
            rx_chakra.heading("Mission Control", size="4xl"),
            rx_chakra.text(f"Robots Online: {State.robots.length()}"),
            rx_chakra.responsive_grid(
                rx.foreach(State.robots.items(), lambda item: robot_card(item[0], item[1])),
                columns=[1, 2, 3],
                spacing="4",
                width="100%",
            ),
            rx.recharts.scatter_chart(
                rx.recharts.x_axis(data_key="x", type_="number", domain=["auto", "auto"], label={"value": "X Coordinate", "position": "insideBottom", "offset": -5}),
                rx.recharts.y_axis(data_key="y", type_="number", domain=["auto", "auto"], label={"value": "Y Coordinate", "position": "insideLeft", "angle": -90}),
                rx.recharts.scatter(data_key="id", fill="#8884d8"),
                data=State.robot_locations,
                width=500,
                height=300,
                margin={'top': 20, 'right': 20, 'bottom': 20, 'left': 20}
            ),
            spacing="5",
        ),
        height="100vh",
    )

def audits():
    return rx_chakra.center(
        rx_chakra.vstack(
            rx_chakra.heading("Safety Audits", size="4xl"),
            rx_chakra.text(f"Incidents: {State.incidents.length()}"),
            rx.foreach(State.incidents, lambda incident:
                rx_chakra.card(
                    rx_chakra.vstack(
                        rx_chakra.heading(f"Incident ID: {incident.get('id', 'N/A')}", size="lg"),
                        rx_chakra.text(f"Type: {incident.get('type', 'N/A')}"),
                        rx_chakra.text(f"Robot: {incident.get('robot_id', 'N/A')}"),
                        rx_chakra.text(f"Timestamp: {incident.get('timestamp', 'N/A')}"),
                    )
                )
            ),
            spacing="5",
        ),
        height="100vh",
    )

# Add page routes and create the app.
app = rx.App()
app.add_page(index, on_load=State.start_mqtt_client)
app.add_page(audits)
