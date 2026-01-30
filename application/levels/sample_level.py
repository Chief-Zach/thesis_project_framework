from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response, JSONResponse
from json import JSONDecodeError
from app.utils.extensions import generate_button, templates, FormGroup, FormData, generate_hidden_text
from app.utils.page import Page
import json
from config import get_config
from typing import Annotated, Optional
from fastapi import Form

config = get_config()


password_level = Page("Password Problems")
password_level.load_scripts({"password_form": "password_form.js"})
game = password_level.route

async def verify(request: Request):
    try:
        data = await request.json()
        user_cookie = request.cookies.get("user")
        if password_level.parameterization.parameterize_flag(user_cookie, password_level.level_code) == data.get("flag", None):
            return {"success": True}
        else:
            return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    except (JSONDecodeError, KeyError):
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

async def instructions(request: Request):
    text = "Your username is admin and your password is password."
    button = generate_button("Frontend", f"{config.URL}{password_level.url_prefix}/frontend")

    response = templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": password_level.name,
                                    "text": text, "primary_button": button})

    return response

password_level.set_functions(verify=verify, instructions=instructions)

@game.post("/login", response_class=JSONResponse)
def login(request: Request, username: Annotated[Optional[str], Form()] = None,
          password: Annotated[Optional[str], Form()] = None):
    user_cookie = request.cookies.get("user", None)

    if username == "admin" and password == "password":
        return JSONResponse(f"Login Success "
                            f"{password_level.parameterization.parameterize_flag(user_cookie, password_level.level_code)}",
                            status_code=200)
    return JSONResponse("Incorrect Password", status_code=403)


@game.get("/frontend", response_class=HTMLResponse)
async def frontend(request: Request):
    user_cookie = request.cookies.get("user", None)

    if user_cookie is None:
        return Response(500)

    form_groups = [FormGroup("username", "text", "usernameInput", "Username"),
        FormGroup("password", "password", "passwordInput", "Password")]

    form_data = FormData(f"{config.URL}{password_level.url_prefix}/login", form_groups).generate_form()

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": password_level.name
                                      ,"form_data": form_data,
                                      "scripts": password_level.scripts["password_form"]})
