"""Broken Authentication password brute-force challenge level.

Solution:

1. The username is known: admin.
2. Run a form brute-force tool with:
   - target endpoint `/games/broken_authentication_password_attacks/auth`
   - form fields `username` and `password`
   - header `Cookie: user=<your_cookie>`
   - failure matcher `Invalid credentials`
    Command: 
        hydra -l admin -P wordlist.txt -s 8000 -t 1 localhost http-post-form '/games/broken_authentication_password_attacks/auth:username=^USER^&password=^PASS^:H=Cookie\:user=<your_cookie>:F=Invalid credentials' -V
"""


from json import JSONDecodeError
from typing import Annotated, Optional

from fastapi import Form, Request
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from app.utils.extensions import FormData, FormGroup, generate_button, templates
from app.utils.page import Page
from config import get_config

config = get_config()

broken_auth_password_attacks = Page(
    "Broken Authentication Password Attacks",
    default_hint=(
        "Automate password attempts against the auth endpoint. "
        "Ensure your request includes the user cookie and key off the failure response text."
    ),
)
broken_auth_password_attacks.load_scripts({"password_form": "password_form.js"})
game = broken_auth_password_attacks.route

# Intentionally weak credentials for educational brute-force training.
TARGET_USERNAME = "admin"
TARGET_PASSWORD = "sunshine"


async def verify(request: Request):
    try:
        data = await request.json()
        user_cookie = request.cookies.get("user")
        expected_flag = broken_auth_password_attacks.parameterization.parameterize_flag(
            user_cookie, broken_auth_password_attacks.level_code
        )

        if data.get("flag") == expected_flag:
            return {"success": True}
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}
    except (JSONDecodeError, KeyError):
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}


async def instructions(request: Request):
    text = (
        "Broken Authentication - Password Attacks (Medium).<br><br>"
        "This login endpoint has no account lockout and allows unlimited attempts.<br><br>"
        "Objective: discover valid credentials for the auth endpoint.<br><br>"
        "Known username: <b>admin</b><br>"
        "Target endpoint: <b>/games/broken_authentication_password_attacks/auth</b><br>"
        "Failure text: <b>Invalid credentials</b><br>"
        "Required header: <b>Cookie: user=&lt;your_cookie&gt;</b><br>"
    )

    button = generate_button(
        "Frontend",
        f"{config.URL}{broken_auth_password_attacks.url_prefix}/frontend",
    )

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": broken_auth_password_attacks.name,
            "text": text,
            "primary_button": button,
        },
    )


broken_auth_password_attacks.set_functions(verify=verify, instructions=instructions)


@game.post("/auth", response_class=JSONResponse)
def auth(
    request: Request,
    username: Annotated[Optional[str], Form()] = None,
    password: Annotated[Optional[str], Form()] = None,
):
    user_cookie = request.cookies.get("user", None)

    # Require the framework user cookie so brute-force tooling must supply it explicitly.
    if user_cookie is None:
        return JSONResponse("Unauthorized", status_code=401)

    if username == TARGET_USERNAME and password == TARGET_PASSWORD:
        flag = broken_auth_password_attacks.parameterization.parameterize_flag(
            user_cookie, broken_auth_password_attacks.level_code
        )
        return JSONResponse(
            f"Authentication successful. Flag: {flag}",
            status_code=200,
        )

    return JSONResponse("Invalid credentials", status_code=200)


@game.get("/frontend", response_class=HTMLResponse)
async def frontend(request: Request):
    user_cookie = request.cookies.get("user", None)

    if user_cookie is None:
        return JSONResponse("Missing user cookie", status_code=500)

    form_groups = [
        FormGroup("username", "text", "usernameInput", "Username", placeholder="admin"),
        FormGroup("password", "password", "passwordInput", "Password"),
    ]

    form_data = FormData(
        f"{config.URL}{broken_auth_password_attacks.url_prefix}/auth", form_groups
    ).generate_form()

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": broken_auth_password_attacks.name,
            "text": "Authenticate to retrieve the flag.",
            "subtext": "This endpoint intentionally allows unlimited password attempts.",
            "form_data": form_data,
            "scripts": broken_auth_password_attacks.scripts["password_form"],
        },
    )
