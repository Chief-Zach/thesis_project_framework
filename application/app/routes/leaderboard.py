from ..utils.extensions import templates, Table
from requests import Request
from ..utils.page import Page
from ..models.user import User, Level

from ..config import get_config
from ..utils.extensions import templates
from typing import Dict, List

config = get_config()

async def instructions(request: Request):
    if config.MONGO:
        leaderboard_data: List[Dict[str, str]] = await User.generate_leaderboard()

        if len(leaderboard_data) == 0:
            table_data = "<p>There is no one in the leaderboard to show"
            return templates.TemplateResponse(request=request, name="board.html",
                                              context={"table_data": table_data})

        table_data = Table([{"ID": str(x["_id"]),
                             "Completed": x["completed_count"]
                             }
                            for x in leaderboard_data])


    else:
        table_data = "<h1>Please enable databases to see the leaderboard</h1>"
        return templates.TemplateResponse(request=request, name="board.html",
                                          context={"table_data": table_data})

    return templates.TemplateResponse(request=request, name="board.html", context={"table_data": table_data.get_html(),
                                                                                   "header": "Leaderboard"})

not_game_class = Page("Leaderboard", instructions=instructions, is_game=False)