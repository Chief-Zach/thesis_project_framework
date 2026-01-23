import json
from json import JSONDecodeError
from typing import Annotated, Optional

from fastapi import Form
from starlette.responses import JSONResponse

from ..utils.extensions import FormGroup, FormData
from ..utils.extensions import generate_hidden_text
from fastapi import Request
from starlette.responses import HTMLResponse

from ..utils.aes_service import aes_service
import string
import secrets
from ..utils.extensions import generate_button
from ..utils.page import Page
from ..config import get_config
from ..utils.extensions import templates
from random import choice

from ..utils.parameterization import parameterization

config = get_config()

with open(f"{config.BASE_DIR}/src/static/data/passwords.json") as file:
    password_options = json.load(file)
    password_keys = list(password_options)

default_hint = ("Look through the source code for the page to see if you find anything interesting. If you find anything,"
                "what do you think it is?")

game_class = Page("Hard Hashing", default_hint=default_hint)

game_class.load_scripts({"password_form": "password_form.js"})

async def instructions(request: Request):
    text = ("You come across a website that looks like it is still in development, or just never reached production. "
            "In order to access the page however, there is a username and password prompt. Since you know that sites in "
            "development tend to be insecure, you decide to look around.")


    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    response = templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": game_class.name,
                                    "text": text, "primary_button": button})

    if not request.cookies.get(game_class.string_name, False):
        cookie, _ = generate_cookie(request.cookies.get("user"))
        response.set_cookie(game_class.string_name, cookie)


    return response

async def verify(request: Request):
    try:
        data = await request.json()
        user_cookie = request.cookies.get("user")
        if parameterization.parameterize_flag(user_cookie, game_class.level_code) == data.get("flag", None):
            return {"success": True}
        else:
            return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    except (JSONDecodeError, KeyError):
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}



game_class.set_functions(instructions, verify)

game = game_class.route

def check_pass(request: Request, password) -> bool:

    cookie = request.cookies.get(game_class.string_name, None)

    if cookie is None:
        return False
    correct_password = get_password(cookie)

    if password == correct_password:
        return True
    return False

def generate_cookie(user_cookie: str):
    user_password = choice(password_keys)
    encrypted = parameterization.parameterize_with_data(user_cookie, {"user_password": user_password})

    return encrypted, user_password

def get_password(cookie):
    data = parameterization.get_data_from_parameterization(cookie)

    user_password = data.get("input_data").get("user_password", None)
    if user_password is not None:
        return user_password
    else:
        print(data)
        raise Exception("Error with parameterization")

@game.post('/login', response_class=JSONResponse)
def login(request: Request, password: Annotated[Optional[str], Form()]=None):

    if not password:
        return JSONResponse("All fields were not filled out", status_code=400)

    elif check_pass(request, password):
        user_cookie = request.cookies.get("user")
        return JSONResponse(f"Login Success "
                            f"{parameterization.parameterize_flag(user_cookie, game_class.level_code)}", status_code=200)
    else:
        return JSONResponse("Incorrect Password", status_code=403)

@game.get('/frontend', response_class=HTMLResponse)
async def serve_frontend(request: Request):
    user_cookie = request.cookies.get("user")
    cookie = request.cookies.get(game_class.string_name, None)

    form_groups = [FormGroup("password", "password", "passwordInput", "Password")]

    form_data = FormData(f"{config.URL}{game_class.url_prefix}/login", form_groups).generate_form()

    set_cookie = False

    if cookie is None:
        set_cookie = True
        cookie, password = generate_cookie(user_cookie)
        password_hash = password_options[password]

    else:
        password = get_password(cookie)

        password_hash = password_options[password]

    hidden_text = generate_hidden_text(f"DO NOT SHARE {password_hash}")

    response = templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"form_data": form_data,
                                    "header": "Login", "scripts": game_class.scripts["password_form"],
                                    "hidden_text": hidden_text})

    if set_cookie:
        response.set_cookie(game_class.string_name, cookie)

    return response