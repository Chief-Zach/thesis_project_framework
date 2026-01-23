import time

from fastapi import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from hashlib import sha256
import json
from ..utils.page import Page
from ..utils.extensions import generate_button
from ..config import get_config
from ..utils.extensions import templates
from ..utils.parameterization import parameterization
from typing import Union

config = get_config()

default_hint = ("Everything you need is in the 'super_secure_request' POST request. Pay less attention to the hash "
                "itself, but more how to get to the hash with the data you have."
                "You can use a tool like <a href=https://www.tunnelsup.com/hash-analyzer/>TunnelsUp</a> to determine hash types.")

game_class = Page("Random Text", default_hint=default_hint)

game_class.load_scripts({"connection": "game_3.js"})

async def instructions(request: Request):
    text =("You are scrolling around on your favourite social media site when you see some weird requests "
                    "coming across your network tab. Can you reverse engineer whats happening and successfully make a "
                    "connection to the backend? get_connection_data"
                    " will return you some interesting data, and you can access the network tab of your social media "
                    "page on the frontend. ")

    subtext = ("Hint: You cannot use the outputs "
                    "from get_connection_data to solve this, they are encrypted, and the answer is not found in the "
                    "HTML or JS code viewable on the frontend.")

    button = generate_button("Frontend", f"{config.URL}{game_class.url_prefix}/frontend")

    secondary_button = generate_button("Get Connection Data",
                                       f"{config.URL}{game_class.url_prefix}/get_connection_data", primary=False)

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"header": game_class.name,
                                    "text": text, "subtext": subtext, "primary_button": button, "secondary_button": secondary_button})

async def verify(request: Request):
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    user_cookie = request.cookies.get("user")

    if data.get("flag", None) == parameterization.parameterize_flag(user_cookie, game_class.level_code):
        return {"success": True}

    else:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

game_class.set_functions(instructions, verify)

game = game_class.route

def valid_hash(data) -> Union[str, bool]:
    if 'time' in data:
        try:
            num_time = int(data['time'])
        except ValueError:
            return False

        if int(time.time()) - num_time < 30000:
            buff_time = data['time'].encode('utf-8')
            hashed_time = sha256(buff_time).hexdigest()
            if hashed_time == data['hash']:
                return "user"
            else:
                buff_time_plus_string = (data['time'] + "anlco8e7hc82q7c98027345oihbas0d897").encode('utf-8')
                hashed_time_plus_string = sha256(buff_time_plus_string).hexdigest()
                if hashed_time == data['hash'] or hashed_time_plus_string == data['hash']:
                    return "admin"

    return False

@game.get('/get_connection_data', response_class=JSONResponse)
async def get_connection_data():
    curr_time = int(time.time())
    hashed_time = (str(curr_time) + "anlco8e7hc82q7c98027345oihbas0d897").encode('utf-8')
    payload = {
        'time': str(curr_time),
        'hash': sha256(hashed_time).hexdigest(),
        'imagePath': 'secure_image.png'
    }

    return {"payload": payload}

@game.get('/frontend', response_class=HTMLResponse)
async def serve_frontend(request: Request):
    button = generate_button("Post", element_id="post_listener")

    return templates.TemplateResponse(request=request, name=config.TEMPLATE, context={"scripts": game_class.scripts["connection"],
                                    "header": "Post Here!", "primary_button": button})


@game.post('/super_secure_request', response_class=Response)
async def time_hashing(request: Request):
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        resp = Response("Permission Denied")
        resp.status_code = 403
        return resp

    if not all([data.get('imagePath', None), data.get('time', None), data.get('hash', None)]):
        return JSONResponse({"error": "Malformed request"}, status_code=400)

    if valid_hash(data) == "admin":
        return JSONResponse(f"Successfully posted image {data['imagePath']}. Now try it yourself for a flag!")

    elif valid_hash(data) == "user":
        user_cookie = request.cookies.get("user")
        return JSONResponse(f"Successfully posted image {data['imagePath']}. Here is your flag "
                            f"{parameterization.parameterize_flag(user_cookie, game_class.level_code)}")

    else:
        resp = Response("Permission Denied")
        resp.status_code = 403
        return resp
