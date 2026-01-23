from typing import Annotated, Optional

from fastapi import Request, Form
from starlette.responses import HTMLResponse, JSONResponse

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

default_hint = ("After running the simulated request, what data do you have access to? Can you use any of this data to "
                "gain access to the application?")

game_class = Page("Password Potential", default_hint=default_hint)

game_class.load_scripts({"connection": "password_potential.js", "hash_pass": "hash_passwords.js"})

async def instructions(request: Request):
    text = ("You are sitting in your local coffee shop and are running a network analyzer. You notice a plain text request "
            "come across the network. This request can be simulated by pressing the 'Get Simulated Request' button below. "
            "The request appears to be from a login page, that is accessible through the 'Frontend' button below. "
            "You can try out your credentials on the login page, before submitting it to verify. When submitting, "
            "submit your username and password as 'email' and 'password' in the POST data.")


    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    secondary_button = generate_button("Simulated Request", primary=False,
                                       element_id="simulate_listener")

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": game_class.name,
                                    "text": text, "primary_button": button, "secondary_button": secondary_button,
                                    "scripts": game_class.scripts["connection"]})

async def verify(request: Request):
    try:
        data = await request.json()
        user_cookie = request.cookies.get("user")
        if data.get("flag") == parameterization.parameterize_flag(user_cookie, game_class.level_code):
            return {"success": True}
        else:
            return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    except (json.JSONDecodeError, KeyError):
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

game_class.set_functions(instructions, verify)

game = game_class.route


def check_pass(request: Request, email, password) -> bool:
    correct_password = parameterization.parameterize_flag(request.cookies.get("user"), game_class.level_code)
    if (password == correct_password and
            email == "admin@admin.com"):
        return True
    return False

@game.post('/login', response_class=JSONResponse)
def login(request: Request, email: Annotated[Optional[str], Form()]=None,
          password: Annotated[Optional[str], Form()]=None):

    if request.headers.get("accept-language") == "tlh-Latn":
        flag = "FakeFlag"
    else:
        user_cookie = request.cookies.get("user")
        flag = parameterization.parameterize_flag(user_cookie, game_class.level_code)
    if not email or not password:
        return JSONResponse("All fields were not filled out", status_code=400)
    elif check_pass(request, email, password):
        return JSONResponse(f"Login Success, here is your flag {flag}", status_code=200)
    else:
        return JSONResponse("Incorrect Password", status_code=403)

@game.get('/get_data')
async def simulate_request(request: Request):

    return JSONResponse({"email": "admin@admin.com",
                         "hashed_password": parameterization.parameterize_flag(request.cookies.get("user"), game_class.level_code)})

@game.get('/frontend', response_class=HTMLResponse)
async def serve_frontend(request: Request):
    form_groups = [FormGroup("email", "email", "emailInput", "Email"),
                   FormGroup("password", "password", "passwordInput", "Password")]

    form_data = FormData(f"{config.URL}{game_class.url_prefix}/login", form_groups).generate_form()

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"form_data": form_data,
                                    "header": "Login", "scripts": game_class.get_scripts(["hash_pass"])})