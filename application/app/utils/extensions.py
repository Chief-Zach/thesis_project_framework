import uuid

from fastapi import Request
from starlette.datastructures import Headers
from fastapi.templating import Jinja2Templates
from typing import List, Union, Dict, Any, Tuple
from ..models import User
from loguru import logger
import numpy as np
import html

templates = Jinja2Templates(directory="src/templates")


def get_cookie(request: Request):
    return request.cookies.get("user", None)


def get_ip(headers: Headers):
    return headers.get("X-Real-IP", "127.0.0.1")


async def generate_user_cookie(request: Request, config):
    cookie = str(uuid.uuid4())

    logger.info(request.headers)
    if config.MONGO:
        await User.create_user(cookie, get_ip(request.headers))

    return cookie


class Table:
    def __init__(self, data: Union[
        Dict[str, List[str]], List[Union[List, Tuple]], List[Dict[str, Any]], Tuple[Union[List, Tuple]]],
                 headers: Union[List, None] = None, safe=False):
        self.data = data
        self.headers = headers
        self.safe = safe
        if isinstance(self.data, dict) and isinstance(list(self.data.values())[0], list):
            self.is_dict = True
            self.is_list = False
            self.headers = list(self.data.keys())

        elif isinstance(self.data[0], list):
            self.is_list = True
            self.is_dict = False

        else:
            self.is_list = False
            self.is_dict = False

        if self.headers is None and self.is_list is True:
            raise Exception("Items cannot be list, and pass no headers")

    def _generate_header(self):
        if self.headers is None:
            self.headers = [x for x in self.data[0]]

        header_str = "<thead>"
        for header in self.headers:
            header_str += f"<th>{html.escape(str(header)) if not self.safe else header}</th>"
        header_str += "</thead>"
        return header_str

    def get_html(self):
        data_str = '<table class="table">'
        data_str += self._generate_header()

        if self.is_list:
            for data in self.data:
                for data_point in data:
                    data_str += "<tr>"
                    data_str += f"<td>{html.escape(str(data_point))if not self.safe else data_point}</td>"
                    data_str += f"<td>{html.escape(str(data_point))if not self.safe else data_point}</td>"
                    data_str += f"<td>{html.escape(str(data_point))if not self.safe else data_point}</td>"
                    data_str += "</tr>"

        elif self.is_dict:

            max_length = max(len(v) for v in self.data.values())

            for value in range(max_length):
                data_str += "<tr>"
                for key in self.headers:
                    try:
                        data_str += f"<td>{html.escape(str(self.data[key][value])) if not self.safe else self.data[key][value]}</td>"
                    except IndexError:
                        data_str += "<td>None Yet</td>"

                data_str += "</tr>"


        else:
            keys = list(self.data[0].keys())

            for data in self.data:
                data_str += "<tr>"
                for key in keys:
                    data_str += f"<td>{html.escape(str(data[key])) if not self.safe else data[key]}</td>"
                data_str += "</tr>"

        data_str += "</table>"

        return data_str


def quote_string(string: str):
    return f'"{string}"'


def generate_button(text, link=None, primary=True, element_id=None):
    if primary:

        return f'<button type="button" {"" if not element_id else f"id={element_id}"} {"" if not link else "onclick=location.href=" + quote_string(link)} class="btn btn-primary btn-lg px-4 gap-3">{text}</button>'
    else:
        return f'<button type="button" {"" if not element_id else f"id={element_id}"} {"" if not link else "onclick=location.href=" + quote_string(link)} class="btn btn-outline-secondary btn-lg px-4">{text}</button>'


def generate_hidden_text(string: str, element_id: str = None):
    return f'<p class="mb-4" id="{element_id if element_id is not None else "hidden"}" hidden>{string}</p>'


class FormGroup:
    def __init__(self, name, input_type, element_id, label_text, placeholder=None, required=True, rows=1):
        self.name = name
        self.input_type = input_type
        self.element_id = element_id
        self.label_text = label_text
        self.required = required
        self.rows = rows
        if placeholder is None:
            self.placeholder = self.label_text
        else:
            self.placeholder = placeholder

    def get_required(self):
        return 'required' if self.required else ''

    def generate_form_group(self):
        form_group = '<div class="container mb-2">'
        form_group += '<div class="card p-2 shadow">'

        form_group += '<div class="form-group">\n'
        form_group += f'\t<label for="{self.element_id}">{self.label_text}</label>\n'
        if self.rows > 1:
            form_group += (
                f'\t<textarea type="{self.input_type}" class="form-control" id="{self.element_id}" name="{self.name}" '
                f'placeholder="{self.placeholder}" {self.get_required()} rows={self.rows}></textarea>\n')

        else:
            form_group += (
                f'\t<input type="{self.input_type}" class="form-control" id="{self.element_id}" name="{self.name}" '
                f'placeholder="{self.placeholder}" {self.get_required()}>\n')
        form_group += '</div>\n</div>\n</div>\n'
        return form_group


class FormData:
    def __init__(self, endpoint, groups: List[FormGroup], method="POST", button_text="Submit", hashing=True):
        self.endpoint = endpoint
        self.groups = groups
        self.method = method
        self.hashing = hashing
        self.button_text = button_text
        self._completed_form = None

    def generate_form(self):
        if self._completed_form is not None:
            return self._completed_form
        else:
            form_data = f'<form action="{self.endpoint}" method="{self.method}" id="loginForm">\n'
            for group in self.groups:
                form_data += group.generate_form_group()

            form_data += f'<button type="submit" class="btn btn-primary">{self.button_text}</button>\n'
            form_data += '</form>'
        return form_data

class Accordian:
    def __init__(self, content: Dict[str, Any], element_id, stay_expanded=False, safe=False):
        self.content = content
        self.element_id = element_id
        self.stay_expanded = stay_expanded
        self.safe = safe

    def _get_data_html(self):
        inner_str = ""
        for count, data in enumerate(self.content):
            inner_str += '<div class="accordion-item">'
            inner_str += '<h2 class="accordion-header">'
            inner_str += '<button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"'
            inner_str += f' data-bs-target="#collapse{count}" aria-expanded="false" aria-controls="collapse{count}">'
            inner_str += html.escape(str(data)) if not self.safe else str(data)
            inner_str += '</button>'
            inner_str += '</h2>'

            inner_str += f'<div id="collapse{count}" class="accordion-collapse collapse" data-bs-parent="#{self.element_id}">'
            inner_str += '<div class="accordion-body">'
            inner_str += self.content[data]
            inner_str += "</div></div></div>"

        return inner_str

    def get_html(self):
        data_str = f'<div class="accordion" id="{self.element_id}">'
        data_str += self._get_data_html()
        data_str += "</div>"

        return data_str
