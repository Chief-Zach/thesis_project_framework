_config = None

def set_config(config):
    global _config
    _config = config

def get_config():
    global _config
    if _config is None:
        raise Exception("Config was not set by app.py")
    return _config