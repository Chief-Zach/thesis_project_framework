import re
from typing import Annotated, Optional

from fastapi import Form, Request
from fastapi.responses import HTMLResponse

from app.utils.extensions import FormData, FormGroup, generate_button, generate_hidden_text, templates
from app.utils.page import Page
from config import get_config

config = get_config()

reflected_xss_post = Page(
    "Reflected XSS Post",
    default_hint=(
        "Submit HTML/JS in the comment field so it is reflected back. "
        "A common test payload is <script>alert(1)</script>."
    ),
)
game = reflected_xss_post.route


def looks_like_xss(payload: str) -> bool:
    if payload is None:
        return False

    lowered = payload.lower()
    patterns = [
        r"<script",
        r"onerror\\s*=",
        r"onload\\s*=",
        r"javascript:",
    ]

    return any(re.search(pattern, lowered) for pattern in patterns)


async def instructions(request: Request):
    text = (
        "Cross-site Scripting - Reflected (POST), easy difficulty.<br><br>"
        "To solve this bug, execute any custom JavaScript by injecting it through the POST request submitted "
        "by this page.<br>"
        "Note: It is recommended to use <b>alert(1)</b> as your test script because it is easy to spot."
    )

    button = generate_button("Open Frontend", f"{config.URL}{reflected_xss_post.url_prefix}/frontend")

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": reflected_xss_post.name,
            "text": text,
            "primary_button": button,
        },
    )


async def verify(request: Request):
    try:
        data = await request.json()
    except Exception:
        return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}

    user_cookie = request.cookies.get("user")
    expected_flag = reflected_xss_post.parameterization.parameterize_flag(user_cookie, reflected_xss_post.level_code)

    if data.get("flag") == expected_flag:
        return {"success": True}

    return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}


reflected_xss_post.set_functions(instructions=instructions, verify=verify)


@game.get("/frontend", response_class=HTMLResponse)
async def frontend(request: Request):
    form_groups = [
        FormGroup(
            name="comment",
            input_type="text",
            element_id="commentInput",
            label_text="Leave a comment",
            placeholder="Try a custom Javascript payload",
            required=True,
            rows=4,
        )
    ]

    form_html = FormData(
        endpoint=f"{config.URL}{reflected_xss_post.url_prefix}/reflect",
        groups=form_groups,
        method="POST",
        button_text="Submit Comment",
    ).generate_form()

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": reflected_xss_post.name,
            "text": "Post a comment. The server reflects your POST body into the page.",
            "form_data": form_html,
        },
    )


@game.post("/reflect", response_class=HTMLResponse)
async def reflect_comment(request: Request, comment: Annotated[Optional[str], Form()] = None):
    user_cookie = request.cookies.get("user")
    expected_flag = reflected_xss_post.parameterization.parameterize_flag(user_cookie, reflected_xss_post.level_code)

    reflected_text = comment or ""
    solved = looks_like_xss(reflected_text)

    # Intentionally unsafe reflection for challenge training.
    result_text = f"You posted: {reflected_text}"
    
    if solved:
        result_text += f"<br><br><strong>XSS Detected!</strong>"
        subtext = "Submit this flag: " + expected_flag
    else:
        subtext = "No script-like payload detected yet. Keep testing reflected POST input."

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": reflected_xss_post.name,
            "text": "Reflected response:",
            "result_text": result_text,
            "subtext": subtext,
            "primary_button": generate_button("Back to Frontend", f"{config.URL}{reflected_xss_post.url_prefix}/frontend"),
        },
    )
