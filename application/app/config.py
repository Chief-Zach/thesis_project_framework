from pathlib import Path
from loguru import logger
from typing import List
class DebugConfig(object):
    VERIFICATION_INPUT = True
    PARAMETERIZE = True
    GAMES: dict = dict()

    URL: str = "http://localhost:8000"
    if VERIFICATION_INPUT:
        TEMPLATE: str = "game_template_verify.html"
    else:
        TEMPLATE: str = "game_template.html"

    LLM: str = "ollama"
    OLLAMA_MODEL: str = "gemma3:4b"
    OLLAMA_PORT: int = 11434
    MONGO: bool = True
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    SOLUTION_EXTENSIONS: List[str] = [".py", ".txt"]
    ADMIN_CODE: bool = False

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