import reflex as rx
import threading
import paho.mqtt.client as paho_mqtt
import json
import asyncio


# Define the main Reflex State
class State(rx.State):
    # Stores real-time telemetry for each robot, keyed by robot ID.
    robots: dict[str, dict] = {}
    # Stores a list of detected safety incidents.
    incidents: list[dict] = []

    # Computed variable for map component
    @rx.var
    def robot_locations(self) -> list[dict]:
        return [
            {'x': r.get('x', 0), 'y': r.get('y', 0), 'id': robot_id}
            for robot_id, r in self.robots.items()
        ]

    def update_robot_data(self, payload: dict):
        robot_id = payload.get('robot_id')
        if robot_id:
            self.robots[robot_id] = payload
            print(f"Updated robot {robot_id}: {payload}")

    def add_incident(self, incident_data: dict):
        self.incidents.append(incident_data)
        print(f"Added incident: {incident_data}")


# MQTT Client Logic
def on_connect(client, userdata, flags, rc):
    print(f"MQTT Connected with result code {rc}")
    client.subscribe("robots/telemetry")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Use add_external_event to update Reflex state from a separate thread
        # Need to ensure the app is running before trying to add external events
        if rx.app.running:
            asyncio.run_coroutine_threadsafe(
                State.update_robot_data(State, payload),
                asyncio.get_event_loop() # Ensure this is the correct event loop
            )
        else:
            print("Reflex app not running, skipping state update.")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def mqtt_thread_loop(app_state_class):
    client = paho_mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("mosquitto", 1883, 60)
    client.loop_forever()

def start_mqtt_client():
    # Only start the MQTT client thread once
    if not hasattr(State, '_mqtt_thread_started'):
        mqtt_thread = threading.Thread(target=mqtt_thread_loop, args=(State,))
        mqtt_thread.daemon = True
        mqtt_thread.start()
        State._mqtt_thread_started = True
        print("MQTT client thread started.")

# Start the MQTT client when the app initializes
rx.app.on_load(start_mqtt_client)


# UI definition
def index():
    return rx.center(
        rx.vstack(
            rx.heading("Mission Control", size="9"),
            rx.text(f"Robots Online: {len(State.robots)}"),
            rx.foreach(State.robots.items(), lambda robot_id, robot_data:
                rx.card(
                    rx.vstack(
                        rx.heading(f"Robot ID: {robot_id}", size="5"),
                        rx.text(f"X: {robot_data.get('x', 'N/A')}, Y: {robot_data.get('y', 'N/A')}"),
                        rx.text(f"Battery: {robot_data.get('battery', 'N/A')}V"),
                        rx.text(f"Status: {robot_data.get('status', 'N/A')}"),
                    )
                )
            ),
            rx.recharts.scatter_chart(
                data=State.robot_locations,
                data_key="id",
                x_data_key="x",
                y_data_key="y",
                width=500,
                height=300,
                margin={'top': 20, 'right': 20, 'bottom': 20, 'left': 20}
            ),
            spacing="5",
        ),
        height="100vh",
    )

def audits():
    return rx.center(
        rx.vstack(
            rx.heading("Safety Audits", size="9"),
            rx.text(f"Incidents: {len(State.incidents)}"),
            rx.foreach(State.incidents, lambda incident:
                rx.card(
                    rx.vstack(
                        rx.heading(f"Incident ID: {incident.get('id', 'N/A')}", size="5"),
                        rx.text(f"Type: {incident.get('type', 'N/A')}"),
                        rx.text(f"Robot: {incident.get('robot_id', 'N/A')}"),
                        rx.text(f"Timestamp: {incident.get('timestamp', 'N/A')}"),
                    )
                )
            ),
            spacing="5",
        ),
        height="100vh",
    )


# Add page routes
rx.add_page(index, route="/")
rx.add_page(audits, route="/audits")

# Add the Reflex app
app = rx.App(state=State)

# This is a temporary setup to handle external events. In a real Reflex app
# with a custom backend, you would typically use app.api.add_api_route
# for data ingestion and then update the state via a method in State.
# However, for direct MQTT integration, we need to carefully manage the event loop.
# The current approach with asyncio.run_coroutine_threadsafe should work if the
# event loop is correctly managed within Reflex's ASGI server.