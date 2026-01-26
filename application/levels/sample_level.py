from random import sample

from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response
from json import JSONDecodeError
from app.utils.extensions import generate_button, templates, Table
from app.utils.page import Page
import json
from config import get_config

config = get_config()

sample_game = Page("Sample Level") # sample_level
game = sample_game.route

sample_game.load_scripts({"password_form": "password_form.js"})

async def instructions(request: Request):
    text = "This is your instruction text"
    button = generate_button(text="Frontend", link=f"{config.URL}{sample_game.url_prefix}/frontend")

    response = templates.TemplateResponse(request=request, name=config.TEMPLATE,
                                          context=
                                          {
                                              "header": sample_game.name,
                                              "text": text,
                                              "primary_button": button
                                          })

    return response

async def verify(request: Request):
    try:
        data = await request.json()
        user_cookie = request.cookies.get("user")
        if sample_game.parameterization.parameterize_flag(user_cookie, sample_game.level_code) == data.get("flag", None):
            return {"success": True}

        else:
            return {"success": False}
    except:
        return {"success": False}

sample_game.set_functions(instructions, verify)

@game.get("/frontend", response_class=HTMLResponse)
async def frontend(request: Request):
    user_cookie = request.cookies.get("user")

    flag = sample_game.parameterization.parameterize_flag(user_cookie, sample_game.level_code)

    part_size = len(flag) // 5

    parts = [flag[i:i + part_size] for i in range(0, len(flag), part_size)]

    table = Table([{f"Part {number + 1}": part for number, part in enumerate(parts)}])


    return templates.TemplateResponse(request=request, name=config.TEMPLATE,
                                      context={
                                          "header": sample_game.name,
                                          "table": table.get_html()
                                      })

