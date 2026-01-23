import os
from typing import Union, List

from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from .utils import extensions
from .utils.page import Page
from .utils.extensions import generate_user_cookie
from .config import set_config
from loguru import logger
import sys
from .config_models.database import db_config
from contextlib import asynccontextmanager
import asyncio
from .models.user import User
from json import JSONDecodeError

class GameClasses:
    def __init__(self, app, config):
        self.app = app
        self.index = 0
        self.lock = asyncio.Lock()
        self.config = config

    async def register_class_route_with_index(self, game_class: Page):
        async with self.lock:
            game_class.set_index(self.index)
            game_class.set_config(self.config)
            if game_class.is_game:
                self.config.GAMES[self.index] = game_class
                self.index += 1
            self.app.include_router(game_class.route, prefix=game_class.url_prefix)

def lifespan_factory(pages):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        if app.state.config.MONGO:
            await db_config.connect()

        logger.remove()
        logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO", enqueue=True)
        games = GameClasses(app, app.state.config)

        from .routes.start import not_game_class
        await games.register_class_route_with_index(not_game_class)

        from .routes.dashboard import not_game_class
        await games.register_class_route_with_index(not_game_class)

        from .routes.how_to_page import not_game_class
        await games.register_class_route_with_index(not_game_class)

        from .routes.leaderboard import not_game_class
        await games.register_class_route_with_index(not_game_class)

        for page in pages:
            await games.register_class_route_with_index(page)

        yield

    return lifespan

async def create_cookie_if_missing(request: Request, call_next, config):
    if request.url.path.startswith("/static"):
        return await call_next(request)

    user_cookie = request.cookies.get("user", None)
    if user_cookie is None:

        if config.ADMIN_CODE:
            current_url = str(request.url).rstrip('/')
            config_url = config.URL.rstrip('/')

            if request.session.get("lm") == "true" and (
                    current_url == config_url or current_url == (config_url + "/check_code")):
                return await call_next(request)

            else:
                response = RedirectResponse(url=config.URL)
                request.session["lm"] = "true"
                return response

        elif request.method == "POST" and request.url.path.startswith("/games"):
            return Response("Please submit your user cookie when you complete challenges", status_code=405)


        else:
            new_cookie = await generate_user_cookie(request, config)
            response = RedirectResponse(url=config.URL)
            response.set_cookie(key="user", value=new_cookie, httponly=False)
            return response

    if config.MONGO:
        user = await User.get_user(user_cookie)
        if user is not None:
            request.state.user = user

    response = await call_next(request)
    return response


def create_app(config, pages: List[Page]):
    set_config(config)
    app: FastAPI = FastAPI(lifespan=lifespan_factory(pages))

    app.mount("/static", StaticFiles(directory="src/static"), name="static")
    limiter = Limiter(key_func=extensions.get_cookie,
                      default_limits=["2/second", "60/minute"])

    app.state.limiter = limiter
    config.LIMITER = limiter
    app.state.config = config
    app.add_middleware(SlowAPIMiddleware)

    from starlette.middleware.base import BaseHTTPMiddleware

    # Force HTTPS, and forward the headers to NGINX
    class ForceHTTPSMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            # Trust proxy headers for HTTPS detection
            if request.headers.get("x-forwarded-proto") == "https":
                request.scope["scheme"] = "https"
            response = await call_next(request)
            return response


    # Global exception handler for rate-limited routes
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(_, __):
        return JSONResponse(
            {"detail": "Rate limit exceeded"},
            status_code=429
        )

    # Global exception handler for 404 (Page not found)
    @app.exception_handler(404)
    async def no_page_handler(_, __):
        return RedirectResponse("/")

    # Add user cookie if missing
    @app.middleware("http")
    @limiter.exempt
    async def add_cookie_if_missing(request: Request, call_next):
        return await create_cookie_if_missing(request, call_next, config)

    # Deploy welcome page (not needed to be a separate route)
    @app.get('/', response_class=HTMLResponse)
    async def welcome(request: Request):

        launch_modal = request.session.get("lm", "false")

        return extensions.templates.TemplateResponse("welcome.html", {"request": request, "launch_modal": launch_modal})

    # Check code if password protection is enabled
    @app.post('/check_code', response_class=HTMLResponse)
    async def check_code(request: Request):
        try:
            data = await request.json()
            code = data.get("code")
        except JSONDecodeError:
            return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)
        if code is not None and request.session.get("lm", "true"):
            user = await User.get_user_by_code(code)
            if user is not None:
                request.session.clear()
                response = RedirectResponse(url=config.URL, status_code=302)
                response.set_cookie("user", user.user_cookie)
                response.delete_cookie("session")
                return response

        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)

    # CORS policy
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://thesis.zachfrank.dev"
    ]

    # Add the middlewares that we created before, this must be done at the end
    app.add_middleware(ForceHTTPSMiddleware)
    app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

