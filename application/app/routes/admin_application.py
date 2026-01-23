from json import JSONDecodeError
from typing import Annotated, Optional

from fastapi import Request, Form
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

import json
from ..utils.extensions import generate_button, FormGroup, FormData
from ..utils.aes_service import hashing_service, aes_service
from ..utils.page import Page
from ..config import get_config
from ..utils.extensions import templates
from ..utils.parameterization import parameterization
import secrets
import string

config = get_config()

default_hint = "How do applications determine sessions and in rare cases, user level?"

game_class = Page("Admin Application", default_hint=default_hint)

game_class.load_scripts({"connection": "password_potential.js", "hash_pass": "hash_passwords.js"})

async def instructions(request: Request):
    text = ("You sign into your favourite web application and decide to poke around how they determine who you are. "
            "Your username and password is \"user\" and \"password\"")


    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": game_class.name,
                                    "text": text, "primary_button": button,
                                    "scripts": game_class.scripts["connection"]})

async def verify(request: Request):
    try:
        data = await request.json()
        flag = data.get("flag", None)
    except JSONDecodeError:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    cookie = request.cookies.get("user", None)
    if cookie and parameterization.parameterize_flag(cookie, game_class.level_code) == flag:
        return {"success": True}
    else:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}


game_class.set_functions(instructions, verify)

game = game_class.route

@game.post('/login', response_class=JSONResponse)
def login(request: Request, user: Annotated[Optional[str], Form()]=None,
          password: Annotated[Optional[str], Form()]=None):
    print(user, password)
    if not user or not password:
        return JSONResponse("All fields were not filled out", status_code=400)

    elif user == "user" and password == hashing_service.hash("password").hexdigest():
        response = RedirectResponse(f"{config.URL}{game_class.url_prefix}/page", status_code=302)
        response.set_cookie("admin", value="0")
        return response

    else:
        return JSONResponse("Incorrect Password", status_code=403)

@game.get('/page', response_class=HTMLResponse)
async def serve_page(request: Request):
    admin_cookie = request.cookies.get("admin", None)

    if admin_cookie == '0':
        return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"Header": "User Page",
                                                        "text": "This is your USER page. You do not have admin access"})
    elif admin_cookie == '1':
        return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"Header": "Admin Page",
                                        "text": parameterization.parameterize_flag(request.cookies.get("user"), game_class.level_code)})
    else:
        return RedirectResponse(f"{config.URL}{game_class.url_prefix}/frontend")


@game.get('/frontend', response_class=HTMLResponse)
async def serve_frontend(request: Request):
    form_groups = [FormGroup("user", "user", "userInput", "User"),
                   FormGroup("password", "password", "passwordInput", "Password")]

    form_data = FormData(f"{config.URL}{game_class.url_prefix}/login", form_groups).generate_form()

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"form_data": form_data,
                                    "header": "Login", "scripts": game_class.get_scripts(["hash_pass"])})