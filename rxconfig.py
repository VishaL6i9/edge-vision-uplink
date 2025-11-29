import reflex as rx

class EdgevisionuplinkConfig(rx.Config):
    pass

config = EdgevisionuplinkConfig(
    app_name="edge_vision_uplink_app",
    db_url="mongodb://mongodb:27017/reflex", # Using 'reflex' as the database name
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
    plugins=[rx.plugins.sitemap.SitemapPlugin()],
)
