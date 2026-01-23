import asyncio
from typing import Callable, Union, Dict, List

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import Response, HTMLResponse
from starlette.responses import JSONResponse
from ..utils.extensions import templates
from ..models.user import User
from .exceptions import NoSolutionFound
from .llm_manager import get_llm
from .llm_service import LLMConnector
import secrets

class Page:
    def __init__(self, name: str, instructions: Union[str, Callable] = None,
                 verify: Union[Callable] = None,
                 scripts: Dict[str, str] = None, default_hint: str = None, is_game: bool = True, filename=None):

        self.config = None
        self.llm = None

        self.string_name = name.lower().replace(' ', '_')
        if filename is None:
            self.filename = self.string_name
        else:
            self.filename = filename

        self.is_game = is_game
        self.route = APIRouter()
        self.name = name
        if self.is_game:
            self.url_prefix = f"/games/{self.string_name}"
        else:
            self.url_prefix = f"/{self.string_name}"
        self.index = None
        self.instructions = instructions
        self.verify = verify
        self.default_hint = default_hint
        self.scripts = {}
        self.prompt = None
        self.level_code = secrets.token_hex(15)

        if scripts is not None:
            self.load_scripts(scripts)

    def _register_routes(self):
        if self.instructions:
            self._register_instructions()
        if self.verify:
            self._register_verify()
        self._register_hint()

    def _register_instructions(self):
        @self.route.get('', response_class=HTMLResponse)
        async def instructions(request: Request):
            if isinstance(self.instructions, str):
                return templates.TemplateResponse(request=request, name=self.config.TEMPLATE,
                                                  context={"header": self.name,
                                                           "text": self.instructions})
            else:
                if asyncio.iscoroutinefunction(self.instructions):
                    return await self.instructions(request)
                else:
                    return self.instructions(request)

    def _register_verify(self):
        @self.route.post('/verify', response_class=JSONResponse)
        async def verify(request: Request):
            if self.config.MONGO:
                user: User = request.state.user
                if not await user.is_complete(level=self.name):
                    await user.upsert_request_user(level=self.name, request=request)  # Do not insert if the user
                    # has already won

            if asyncio.iscoroutinefunction(self.verify):
                verify_response = await self.verify(request)
            else:
                verify_response = self.verify(request)
            if verify_response["success"]:
                return await self.success(request)
            else:
                error = verify_response.get("error", None)
                response = self._generate_errors(error)
                return response

    def _register_hint(self):
        @self.route.get('/hint', response_class=JSONResponse)
        async def hint(request: Request):
            user: User = request.state.user

            if self.config.LLM and self.config.MONGO:
                return await self._handle_hint(user, False)
            elif self.default_hint:
                if self.config.MONGO:
                    return await self._handle_hint(user, True, self.default_hint)
                else:
                    return {"payload": self.default_hint}
            else:
                return {"payload": "Please contact the challenge administrator as hints are not enabled"}

    async def _handle_hint(self, user: User, default: bool, default_hint="") -> dict:

        if await user.is_complete(level=self.name):
            return {"payload": "You have already completed this level!"}
        hint_length = await user.get_hint_length(self.name)
        if hint_length > 2:
            return {
                "payload": f"Hint {min(hint_length + 1, 3)}: {await user.get_last_hint(self.name)}", "no_hints": True
            }

        last_requests = await user.get_last_requests(level=self.name)
        if len(last_requests) == 0:
            return {"payload": "You need to make an attempt before getting a hint!"}


        if not default:
            prompt = await self._generate_prompt()

            try:
                hint_data: str = await self.llm.get_hint(
                    prompt=prompt,
                    past_queries=last_requests
                )
            except:
                return {"payload": "Sorry, we are unable to fetch a hint at this time"}

        else:
            hint_data = default_hint

        await user.upsert_hint_user(level=self.name, hint_text=hint_data)
        return {"payload": f"Hint {min(hint_length + 1, 3)}: {hint_data}"}

    def set_index(self, index):
        self.index = index

    def set_config(self, config):
        self.config = config
        if self.config.LLM:
            self.llm: LLMConnector = get_llm(config)
        else:
            self.llm = None

        self._register_routes()

    def set_functions(self, instructions: Union[str, Callable] = None, verify: Callable = None):

        if instructions is not None:
            self.instructions = instructions
            self._register_instructions()
        if verify is not None:
            self.verify = verify
            self._register_verify()

    async def success(self, request: Request):

        if self.config.MONGO:
            user: User = await User.get_user(request.state.user.user_cookie)
            await user.complete_level(level=self.name)

        next_game_object = self.config.GAMES.get(self.index + 1)
        if next_game_object is not None:
            return (f"Congrats! You have successfully completed {self.name}! you can move onto "
                    f"{next_game_object.name} at URL: {self.config.URL}{next_game_object.url_prefix}")

        else:
            return (
                f"Congrats! You have successfully completed {self.name}! That's all the games that we have for "
                f"now. Thank you so much for playing!")

    def load_scripts(self, scripts: Dict[str, str]):
        for script in scripts:
            try:
                with open(f"app/scripts/{scripts[script]}") as f:
                    self.scripts[script] = f.read()

            except FileNotFoundError:
                raise FileNotFoundError(f"There is no file by the name {scripts[script]}")

    def get_scripts(self, script_names: List[str]):
        script_data = ""
        for script in script_names:
            script_text = self.scripts.get(script, None)
            if script_text is not None:
                script_data += script_text + "\n"
            else:
                raise ValueError("The script you are trying to load is not loaded into the class")

        return script_data

    @staticmethod
    def _generate_errors(error):
        if error is not None:
            response_text = error.get("text", None)
            response = JSONResponse({"error": response_text if response_text is not None else ""})
            response_code = error.get("code", None)
            response.status_code = response_code if response_code is not None else 403
        else:
            response = JSONResponse({"error": "Unauthorized"})
            response.status_code = 403

        return response

    async def _generate_prompt(self):
        if self.prompt is None:
            for extension in self.config.SOLUTION_EXTENSIONS:
                try:
                    with open(f"{self.config.BASE_DIR}/solutions/{self.filename}{extension}") as file:
                        solution = file.read()
                        break
                except FileNotFoundError:
                    continue

            if solution is None:
                raise NoSolutionFound(self.filename, self.config.SOLUTION_EXTENSIONS)


            with open(f"{self.config.BASE_DIR}/app/llm_prompt.txt") as file:
                text = file.read()

            formatted_text = text.format(solution=solution)

            self.prompt = formatted_text

        return self.prompt
