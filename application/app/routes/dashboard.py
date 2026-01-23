from ..utils.extensions import templates, Table, Accordian
from fastapi.requests import Request
from ..utils.page import Page
from ..models.user import User, Level
from fastapi.responses import JSONResponse
from ..config import get_config
from typing import Dict
from ..models.user import RequestData
import html

config = get_config()

async def instructions(request: Request):
    if config.MONGO:
        user: User = request.state.user
        level_data: Dict[str, Level] = user.level_data

        if len(level_data) == 0:
            table_data = "<p>Make a level attempt (complete the /verify request) to see your progress</p>"
            return templates.TemplateResponse(request=request, name="board.html",
                                              context={"table_data": table_data})

        else:
            table_data = Table([{"Name": level_data[x].level,
                                 "Hints": str(len(level_data[x].hint_data)),
                                 "Requests": str(len(level_data[x].request_data)),
                                 "Completed": str(level_data[x].completed)} for x in level_data])


    else:
        table_data = "<p>Please enable databases to see the dashboard</p>"
        return templates.TemplateResponse(request=request, name="board.html",
                                          context={"table_data": table_data})

    return templates.TemplateResponse(request=request, name="board.html", context={"table_data": table_data.get_html(),
                                                                                   "header": "Dashboard"})

not_game_class = Page("Dashboard", instructions=instructions, is_game=False)

route = not_game_class.route

def format_requests(request: RequestData):
    return (
        f"<strong>Headers</strong> {html.escape(str(request.headers))}<br>"
         f"<strong>URL</strong>: {html.escape(request.url)}<br>"
         f"<strong>Cookies</strong>: {html.escape(str(request.cookies))}<br>"
         f"<strong>Data</strong>: {html.escape(str(request.data))}<br>"
    )

@route.get('/details')
async def details(request: Request):
    user_cookie = request.cookies.get("user", None)
    if user_cookie is None:
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)

    user_object = await User.get_user(user_cookie)

    if user_object is None:
        return JSONResponse({"success": False, "error": "Unauthorized"}, status_code=403)

    level_data = user_object.level_data
    if len(level_data) == 0:
        table_data = "<p>Make a level attempt (complete the /verify request) to see your progress</p>"
        return templates.TemplateResponse(request=request, name="details.html",
                                          context={"table_data": table_data})

    accordian_data = {}
    for level in level_data:
        requests_data = []
        hints_data = []
        if not level_data[level].hint_data:
            hints_data.append("None Yet")
        else:
            for hint in level_data[level].hint_data:
                hints_data.append(html.escape(hint.hint_text))

        if not level_data[level].request_data:
            requests_data.append("None Yet")
        else:
            for req in level_data[level].request_data:
                requests_data.append(format_requests(req))


        table_data = Table({"Hints": hints_data, "Requests": requests_data}, safe=True)

        accordian_data[level] = table_data.get_html()

    accordian = Accordian(accordian_data, "accordianTables", safe=True)

    return templates.TemplateResponse(request=request, name="details.html", context={"accordian": accordian.get_html()})
