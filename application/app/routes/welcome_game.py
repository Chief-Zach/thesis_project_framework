from fastapi import Request

from ..utils.page import Page
import json
from ..config import get_config

config = get_config()

async def verify(request: Request):
    if request.headers.get("FLAG", None) == "Welcome":
        return {"success": True}

    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    if data.get("Password", None) == "Welcome":
        return {"success": True}
    if data.get("flag", None) == "Welcome":
        return {"success": True}

    return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

instructions = ("Welcome user! The password for this game is "
                   f"'Welcome'. You can submit the password with a POST request to <i>{config.URL}/games/welcome_game/verify</i> "
                f"in the 'FLAG' Header for this game. For future games, the instructions will tell how how to complete the level."
                f"You will always submit flags to <i>{config.URL}/games/game_name/verify</i>. You can learn about "
                "sending web requests programmatically at <a href='https://realpython.com/python-requests/'>"
                "https://realpython.com/python-requests/</a>")

game_class = Page("Welcome Game", instructions=instructions, verify=verify)
game = game_class.route
