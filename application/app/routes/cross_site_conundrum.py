from json import JSONDecodeError
from typing import Annotated, Optional

from fastapi import Request, Form
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response

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

default_hint = "When you make a post, do you see your post REFLECTED back to you?"

game_class = Page("Cross Site Conundrum", default_hint=default_hint)

game_class.load_scripts({"xss_request": "simple_xss_request_obfuscated.js"})

async def instructions(request: Request):
    text = ("Your back on your favorite social media site, but they have added a new feature, posting text. See what text "
            "you can post and what it looks like on the timeline afterwards!")


    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": game_class.name,
                                    "text": text, "primary_button": button})

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

@game.get('/frontend', response_class=HTMLResponse)
async def serve_frontend(request: Request):
    form_groups = [FormGroup("post_text", "text", "textInput", "Write your post here!",
                             placeholder="Your Text", rows=3)]

    form_data = FormData(f"{config.URL}{game_class.url_prefix}/post", form_groups).generate_form()

    text = request.query_params.get("text", None)

    if text is not None:
        return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"form_data": form_data,
                                        "header": "Post", "text": text, "pre_scripts": game_class.get_scripts(["xss_request"])})

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"form_data": form_data,
                                        "header": "Post", "pre_scripts": game_class.get_scripts(["xss_request"])})

@game.post('/post', response_class=RedirectResponse)
async def post_response(request: Request, post_text: Annotated[Optional[str], Form()]=None):
    if post_text:

        return RedirectResponse(f"{config.URL}{game_class.url_prefix}/frontend?text={post_text}", status_code=302)
    return Response(status_code=500)

@game.post('/frontend/{full_path:path}')
async def catch_all(request: Request, full_path: str):
    user_cookie = request.cookies.get("user", None)
    hashed_cookie = hashing_service.hash(user_cookie).hexdigest()

    if full_path == hashed_cookie:
        try:
            data = await request.json()
            code = data.get("poinplkjnsdgf", None)

            if code == hashing_service.hash(hashed_cookie + "qweuyitifbuwef").hexdigest():
                return Response(parameterization.parameterize_flag(user_cookie, game_class.level_code), status_code=200)
        except JSONDecodeError:
            return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}
    else:
        return Response(status_code=403)
