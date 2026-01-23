from ..utils.extensions import templates
from requests import Request

from ..utils.page import Page

async def instructions(request: Request):
    return templates.TemplateResponse(request=request, name="how_to.html")

not_game_class = Page("How To", instructions=instructions, is_game=False)