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
    """
    :arg
    request: The request object from the user request

    :return:
    The users cookie if it exists as a string, else None
    """
    return request.cookies.get("user", None)


def get_ip(headers: Headers):
    """
    :arg
    headers: The headers object from the users request

    :return:
    The users IP as string
    """
    return headers.get("X-Real-IP", "127.0.0.1")


async def generate_user_cookie(request: Request, config):
    """
    :arg
    request: The request object from the user request
    config: The config object

    :return:
    The new user cookie
    """
    cookie = str(uuid.uuid4())

    logger.info(request.headers)
    if config.MONGO:
        await User.create_user(cookie, get_ip(request.headers))

    return cookie


class Table:
    """
    Generates an HTML table based on the data that is provided.
    Data can be provided as a list of lists, but is advised to provide as a dictionary such as:

    {
        column1: [row1, row2, row3, row4],
        column2: [row1, row2, row3, row4]
    }
    """
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
        """
        :return:
        HTML text

        Generate the HTML for the table based on the information passed to the class
        """
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
    """
    :arg
    string: The string to be quoted

    :return:
    Quoted string

    Helper function to quote strings since working with f-strings and HTML can be troublesome
    """
    return f'"{string}"'


def generate_button(text, link=None, primary=True, element_id=None):
    """
    :arg
    text: The text to go in the button
    link: href for where the button click takes the user. Not required
    primary: Boolean for primary button which affects colour. Not required
    element_id: The element ID the button should have. Not required
    :return:
    Button HTML
    """
    if primary:

        return f'<button type="button" {"" if not element_id else f"id={element_id}"} {"" if not link else "onclick=location.href=" + quote_string(link)} class="btn btn-primary btn-lg px-4 gap-3">{text}</button>'
    else:
        return f'<button type="button" {"" if not element_id else f"id={element_id}"} {"" if not link else "onclick=location.href=" + quote_string(link)} class="btn btn-outline-secondary btn-lg px-4">{text}</button>'


def generate_hidden_text(string: str, element_id: str = None):
    """
    :arg
    string: The string to wrap in hidden HTML
    element_id: The element ID of the hidden p tag
    :return:
    Hidden HTML text
    """
    return f'<p class="mb-4" id="{element_id if element_id is not None else "hidden"}" hidden>{string}</p>'


class FormGroup:
    """
    Generates HTML for a form group. This group must be combined with the FormData class to create a working HTML form.
    You must create one of these objects for each input field you want in your form.
    """
    def __init__(self, name, input_type, element_id, label_text, placeholder=None, required=True, rows=1):
        """
        :arg
        name: The key of the form group when it is submitted. Ex. {"password": userpass}
        input_type: The input type for the form, such as "text" or "password"
        element_id: The element ID assigned to this form group
        label_text: The label text shown to the user such as "Password"
        placeholder: The placeholder for the text shown to the user in the input box before typing
        required: Is this form group required to submit the form
        rows: The number of rows for the input box. Way to make input multiline
        """
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

    def _get_required(self):
        return 'required' if self.required else ''

    def generate_form_group(self):
        """
        :return:
        HTML text

        Generate the HTML for the form based on the information passed to the class
        """

        form_group = '<div class="container mb-2">'
        form_group += '<div class="card p-2 shadow">'

        form_group += '<div class="form-group">\n'
        form_group += f'\t<label for="{self.element_id}">{self.label_text}</label>\n'
        if self.rows > 1:
            form_group += (
                f'\t<textarea type="{self.input_type}" class="form-control" id="{self.element_id}" name="{self.name}" '
                f'placeholder="{self.placeholder}" {self._get_required()} rows={self.rows}></textarea>\n')

        else:
            form_group += (
                f'\t<input type="{self.input_type}" class="form-control" id="{self.element_id}" name="{self.name}" '
                f'placeholder="{self.placeholder}" {self._get_required()}>\n')
        form_group += '</div>\n</div>\n</div>\n'
        return form_group


class FormData:
    """
    Form data object to takes in the FormGroup objects to create a working HTML form
    """
    def __init__(self, endpoint, groups: List[FormGroup], method="POST", button_text="Submit"):
        """
        :arg
        endpoint: The endpoint to send the request to on form submission
        groups: The FormGroup objects that make up the form inputs
        method: The method to send the request to the server
        button_text: The submit button text
        """
        self.endpoint = endpoint
        self.groups = groups
        self.method = method
        self.button_text = button_text
        self._completed_form = None

    def generate_form(self):
        """
        :return:
        HTML text

        Generate the HTML for the form based on the information passed to the class
        """
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
    """
    Generate HTML code for accordian menus where each key in a dict is the accordian title, and the value is the text
    in the menu.
    HTML code can be directly injected into
    """
    def __init__(self, content: Dict[str, Any], element_id, safe=False):
        """
        :arg
        content: The content dictionary made up of title: data pairs
        element_id: The element ID of the accordian menu
        safe: If safe, the data will be directly inserted into the HTML. This is unsafe unless the data was pre-screened
        """
        self.content = content
        self.element_id = element_id
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
            inner_str += html.escape(str(self.content[data])) if not self.safe else self.content[data]
            inner_str += "</div></div></div>"

        return inner_str

    def get_html(self):
        """
        :return:
        HTML text

        Generate the HTML for the table based on the information passed to the class
        """

        data_str = f'<div class="accordion" id="{self.element_id}">'
        data_str += self._get_data_html()
        data_str += "</div>"

        return data_str
