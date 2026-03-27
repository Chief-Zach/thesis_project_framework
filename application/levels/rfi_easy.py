import os
from pathlib import Path
from typing import Annotated, Optional

from fastapi import Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.utils.extensions import FormData, FormGroup, generate_button, templates
from app.utils.page import Page
from config import get_config

config = get_config()

rfi_easy = Page(
    "Remote File Inclusion Easy",
    default_hint=(
        "Try accessing files outside the normal folder structure using path traversal. "
        "Hint: Look for sensitive files using paths like ../../filename.txt"
    ),
)
game = rfi_easy.route


async def instructions(request: Request):
    text = (
        "Remote File Inclusion (RFI), easy difficulty.<br><br>"
        "This application has a file viewer that reads files from a restricted directory. "
        "However, it does not properly validate file paths.<br><br>"
        "Your goal: Access a sensitive file outside the normal directory using path traversal. "
        "Reveal the flag by reading the secret file."
    )

    button = generate_button("Open Frontend", f"{config.URL}{rfi_easy.url_prefix}/frontend")

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": rfi_easy.name,
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
    expected_flag = rfi_easy.parameterization.parameterize_flag(user_cookie, rfi_easy.level_code)

    if data.get("flag") == expected_flag:
        return {"success": True}

    return {"success": False, "error": {"code": 403, "text": "Unauthorized"}}


rfi_easy.set_functions(instructions=instructions, verify=verify)


@game.get("/frontend", response_class=HTMLResponse)
async def frontend(request: Request):
    form_groups = [
        FormGroup(
            name="filename",
            input_type="text",
            element_id="filenameInput",
            label_text="File to read",
            placeholder="Try: public_file.txt",
            required=True,
            rows=1,
        )
    ]

    form_html = FormData(
        endpoint=f"{config.URL}{rfi_easy.url_prefix}/read",
        groups=form_groups,
        method="POST",
        button_text="Read File",
    ).generate_form()

    return templates.TemplateResponse(
        request=request,
        name=config.TEMPLATE,
        context={
            "header": rfi_easy.name,
            "text": "Enter a filename to read from the public documents folder.",
            "form_data": form_html,
        },
    )


@game.post("/read", response_class=HTMLResponse)
async def read_file(request: Request, filename: Annotated[Optional[str], Form()] = None):
    user_cookie = request.cookies.get("user")
    expected_flag = rfi_easy.parameterization.parameterize_flag(user_cookie, rfi_easy.level_code)

    if not filename:
        return templates.TemplateResponse(
            request=request,
            name=config.TEMPLATE,
            context={
                "header": rfi_easy.name,
                "text": "File read result:",
                "result_text": "Error: No filename provided.",
                "primary_button": generate_button("Back to Frontend", f"{config.URL}{rfi_easy.url_prefix}/frontend"),
            },
        )

    # Vulnerable file path handling - no proper validation
    base_dir = Path(config.BASE_DIR) / "public_docs"
    requested_path = base_dir / filename

    # Attempt to read the file (vulnerable to path traversal)
    try:
        # Check if file is accessible
        if requested_path.exists() and requested_path.is_file():
            with open(requested_path, "r") as f:
                file_contents = f.read()

            # Check if this is the sensitive file
            solved = "secret file" in file_contents.lower()

            result_text = f"<pre>{file_contents}</pre>"
            subtext = "Submit the revealed flag to /verify using JSON: {{\"flag\": \"...\"}}" if solved else ""

            if solved:
                result_text += f"<br><br><strong>Secret file accessed! Flag: {expected_flag}</strong>"
                subtext = "You found the sensitive file! Submit this flag to verify."

            return templates.TemplateResponse(
                request=request,
                name=config.TEMPLATE,
                context={
                    "header": rfi_easy.name,
                    "text": f"File contents of {filename}:",
                    "result_text": result_text,
                    "subtext": subtext,
                    "primary_button": generate_button("Back to Frontend", f"{config.URL}{rfi_easy.url_prefix}/frontend"),
                },
            )
        else:
            return templates.TemplateResponse(
                request=request,
                name=config.TEMPLATE,
                context={
                    "header": rfi_easy.name,
                    "text": "File read result:",
                    "result_text": f"Error: File {filename} not found.",
                    "subtext": "Try using path traversal to access files outside the public_docs folder.",
                    "primary_button": generate_button("Back to Frontend", f"{config.URL}{rfi_easy.url_prefix}/frontend"),
                },
            )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name=config.TEMPLATE,
            context={
                "header": rfi_easy.name,
                "text": "File read result:",
                "result_text": f"Error: {str(e)}",
                "primary_button": generate_button("Back to Frontend", f"{config.URL}{rfi_easy.url_prefix}/frontend"),
            },
        )
