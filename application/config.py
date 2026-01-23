from pathlib import Path
from loguru import logger
from typing import List

class DebugConfig(object):
    # Edit these to change how the application performs
    VERIFICATION_INPUT = True
    PARAMETERIZE = True

    URL: str = "http://localhost:8000"

    LLM: str = "ollama"
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_PORT: int = 11434
    MONGO: bool = True

    SOLUTION_EXTENSIONS: List[str] = [".py", ".txt"]
    ADMIN_CODE: bool = False

    # Do not change these unless you know what you are doing with the framework
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