from functools import lru_cache
from ..config import get_config
from .llm_service import ChatGPTConnector, ClaudeConnector, OllamaConnector


@lru_cache(maxsize=1)
def _create_llm():
    config = get_config()
    llm_type = getattr(config, "LLM", None)
    if not llm_type:
        raise RuntimeError(
            "LLM is disabled in your config. Enable it in .env if you want to use it."
        )

    llm_type = llm_type.lower()
    if llm_type == "chatgpt":
        return ChatGPTConnector()
    elif llm_type == "claude":
        return ClaudeConnector()
    elif llm_type == "ollama":
        ollama_port = getattr(config, "OLLAMA_PORT", None)
        ollama_model = getattr(config, "OLLAMA_MODEL", None)

        if not all([ollama_port, ollama_port]):
            raise RuntimeError(
                "If you are going to use Ollama, you must define an Ollama port and model to run."
            )

        return OllamaConnector(ollama_port, ollama_model)

    else:
        raise ValueError(f"Unknown LLM type: {llm_type}")

def get_llm():
    return _create_llm()
