from json import JSONDecodeError

from fastapi import Request
from ..utils.extensions import templates
from starlette.responses import HTMLResponse

from ..utils.page import Page
from ..utils.extensions import generate_button
from ..config import get_config

config = get_config()
default_hint = "Never believe your eyes, and always check the response headers!"
game_class = Page("Never Trust Your Eyes", default_hint=default_hint)

async def instructions(request: Request):
    text = ("You've been tasked with pen testing a companies backend API. You know this company has a history "
                    " of using the bad practise of 'Security through Obscurity'. "
                    "Click the button below and look around "
                    "for anything that could grant you access. The endpoint is in perfect working order!")

    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    return templates.TemplateResponse(name=config.TEMPLATE, request=request, context={"header": game_class.name,
                                    "text": text, "primary_button": button}, status_code=200)

async def verify(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    return {"success": data.get("flag") == "YouWillNeverGuessMe"}

game_class.set_functions(instructions=instructions, verify=verify)
game = game_class.route

@game.get('/frontend', response_class=HTMLResponse)
def check_headers(request: Request):
    return templates.TemplateResponse(request=request, name=config.TEMPLATE, status_code=403, headers={"flag": "YouWillNeverGuessMe"})
