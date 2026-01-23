from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from .config_models.database import db_config
import sys
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_config.connect()

    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="INFO", enqueue=True)

    from .routes.home import route
    app.include_router(route)

    yield

def create_app():

    app: FastAPI = FastAPI(lifespan=lifespan)

    app.mount("/static", StaticFiles(directory="src/static"), name="static")
    return app