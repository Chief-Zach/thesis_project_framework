from fastapi.responses import RedirectResponse
from ..utils.page import Page
from ..config import get_config

config = get_config()

not_game_class = Page("Start", is_game=False)

async def start_func(_):
    return RedirectResponse(url=f"{config.URL}{config.GAMES[0].url_prefix}")

not_game_class.set_functions(instructions=start_func)
