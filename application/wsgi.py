# Do not touch this file, it creates the application from your config and your pages
from app.app import create_app
import os
import config
from my_pages import my_pages

def app_factory():
    debug = os.getenv("DEBUG", "1") == "1"

    config.init(debug)
    config_data = config.get_config()
    pages = my_pages()
    return create_app(config_data, pages)