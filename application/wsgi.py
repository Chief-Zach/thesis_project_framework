from app.app import create_app
import os

def app_factory():
    debug = os.getenv("DEBUG", "1") == "1"

    return create_app(is_debug=debug)
