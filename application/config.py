from pathlib import Path
from loguru import logger
from typing import List

class DebugConfig(object):
    # Edit these to change how the application performs
    """
    VERIFICATION_INPUT: Use the template that includes a verification submission box
    PARAMETERIZE: Parameterize the flags so no two users have the same flag (unless otherwise static)
    URL: The base URL of the application, used to make redirects
    LLM: Which LLM you want to use for hints
    OLLAMA_MODEL: The Ollama model you want to use if you have Ollama specified as your LLM
    OLLAMA_PORT: The port Ollama is running on if you have Ollama specified as your LLM
    MONGO: Use the Mongo centralized database
    SOLUTION_EXTENSIONS: The file extensions that your solutions have, in order of priority
    ADMIN_CODE: Weather the user needs an admin code to get a cookie
    """

    VERIFICATION_INPUT = True
    PARAMETERIZE = True

    URL: str = "http://localhost:8000"

    LLM: str = "ollama"
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_PORT: int = 11434
    MONGO: bool = False

    SOLUTION_EXTENSIONS: List[str] = [".py", ".txt"]
    ADMIN_CODE: bool = False

    # Do not change these unless you know what you are doing with the framework
    """
    BASE_DIR: The base directory of your application. Do not change this variable
    TEMPLATE: The base game template file. Do not change this variable
    GAMES: The games dictionary that tracks order and flow. Do not change this variable
    BASE_DIR: The base directory used for locating solutions and other files. Do not change this variable
    """
    if VERIFICATION_INPUT:
        TEMPLATE: str = "game_template_verify.html"
    else:
        TEMPLATE: str = "game_template.html"

    GAMES: dict = dict()

    BASE_DIR: Path = Path(__file__).resolve().parent

class ProductionConfig(DebugConfig):
    URL: str = "https://thesis.zachfrank.dev"
    LLM: str = "ChatGPT"
    MONGO: bool = True

_config = None


def init(is_debug=None):
    global _config
    if _config is None:
        if is_debug is None:
            logger.warning("Debug is not defined, defaulting to True")
            is_debug = True
        _config = DebugConfig() if is_debug else ProductionConfig()

def get_config():
    if _config is None:
        init()
    return _config