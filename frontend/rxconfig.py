import reflex as rx

class EdgevisionuplinkConfig(rx.Config):
    pass

config = EdgevisionuplinkConfig(
    app_name="edge_vision_uplink",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
)
