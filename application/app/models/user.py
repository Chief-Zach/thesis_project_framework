import datetime
from json import JSONDecodeError
from typing import Optional, Dict, List, Union, Any

import pymongo
from pymongo import IndexModel
from beanie import Document
from pydantic import Field, BaseModel
from fastapi import Request
from ..utils import exceptions

class Hint(BaseModel):
    hint_text: str = Field(..., description="Hint text")
    hint_id: int = Field(0, description="ID of the hint")

class RequestData(BaseModel):
    request_id: int = Field(0, description="ID of the request")
    headers: Any = Field(..., description="The headers of the user request")
    url: str = Field(..., description="The url of the user request")
    cookies: Dict[str, str] = Field(..., description="The cookies of the user request")
    data: Dict = Field(..., description="The data of the user request")

    def __str__(self):
        return f"Headers: {self.headers}\nURL: {self.url}\nCookies: {self.cookies}\nData: {self.data}"

class Level(BaseModel):
    level: str = Field(..., description="Level in URL encoding")
    hint_data: List[Hint] = Field(default_factory=list, description="Hint data")
    request_data: List[RequestData] = Field(default_factory=list, description="User request data")
    completed: bool = Field(False, description="Level completion")

class User(Document):

    user_cookie: str = Field(..., description="Cookie the user is provided when creating account")
    user_ip: Optional[str] = Field(None, description="IP for security")
    user_access_code: Optional[str] = Field(None, description="Admin provided code allowing cross device access")
    level_data: Dict[str, Level] = Field(default_factory=dict, description="List of levels the user has interacted with")
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), description="Datetime of object creation")
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC), description="Datetime of object update")

    class Settings:
        name = "users"
        indexes = [
            IndexModel(
                [("user_cookie", pymongo.DESCENDING)],
                name="user_cookie_index_DESCENDING_UNIQUE",
                unique=True
            ),
            IndexModel(
                [("user_access_code", pymongo.DESCENDING)],
                unique=True,
                partialFilterExpression={"user_access_code": {"type": "string"}}
            ),
            IndexModel(
                [("level_data.hint_data.hint_id", pymongo.ASCENDING)],
                name="hint_id_ASCENDING"
            )
        ]

    @classmethod
    async def get_user(cls, cookie):
        return await cls.find_one({"user_cookie": cookie})

    @classmethod
    async def get_user_by_code(cls, code):
        return await cls.find_one({"user_access_code": code})


    @classmethod
    async def generate_leaderboard(cls):

        pipeline = [
            # 1. Match users where level_data is not empty
            {"$match": {"level_data": {"$ne": {}}}},

            # 2. Convert level_data dict to an array of values
            {"$project": {
                "user_cookie": 1,
                "levels_array": {"$objectToArray": "$level_data"}
            }},

            # 3. Count completed levels
            {"$project": {
                "user_cookie": 1,
                "completed_count": {
                    "$size": {
                        "$filter": {
                            "input": "$levels_array.v",
                            "as": "level",
                            "cond": {"$eq": ["$$level.completed", True]}
                        }
                    }
                }
            }},

            {"$sort": {"completed_count": -1}}
        ]

        data = cls.get_pymongo_collection().aggregate(pipeline)

        return [x async for x in data]

    @classmethod
    async def create_level(cls, level, hint_data: Union[None, Hint]=None, completed=False):

        if hint_data is None:
            hint_data = []

        return Level(
            level=level,
            hint_data=hint_data,
            completed=completed
        )

    @classmethod
    async def upsert_hint(cls, cookie: str, level: str, hint_text: str):
        user_obj = await cls.get_user(cookie)
        level_obj = user_obj.level_data.get(level, None)
        if level_obj is None:
            raise exceptions.LevelNotFound(level)

        new_id = len(level_obj.hint_data)

        if new_id < 3:
            new_hint = Hint(hint_id=new_id, hint_text=hint_text)
            level_obj.hint_data.append(new_hint)
            user_obj.updated_at = datetime.datetime.now(datetime.UTC)
            await user_obj.save()

        else: raise exceptions.MaximumHintsReached

    @classmethod
    async def create_user(cls, cookie, ip=None):
        new_user = cls(
            user_cookie=cookie,
            user_ip = ip
        )

        await new_user.insert()
        return new_user

    async def is_complete(self, level):
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            return False

        else:
            return level_obj.completed


    async def get_hint_length(self, level) -> int:
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            return 0

        else:
            return len(level_obj.hint_data)

    async def complete_level(self, level: str):
        level_data = self.level_data.get(level, None)
        if level_data is None:
            raise exceptions.LevelNotFound(level)

        level_data.completed = True
        await self.save()

    async def upsert_hint_user(self, level: str, hint_text: str):
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            raise exceptions.LevelNotFound(level)

        new_id = len(level_obj.hint_data)

        if new_id < 3:
            new_hint = Hint(hint_id=new_id, hint_text=hint_text)
            level_obj.hint_data.append(new_hint)
            self.updated_at = datetime.datetime.now(datetime.UTC)
            await self.save()

        else: raise exceptions.MaximumHintsReached()

    async def upsert_request_user(self, level: str, request: Request):
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            level_obj = self.level_data[level] = await self.create_level(level)

        new_id = min(len(level_obj.request_data), 2)

        try:
            json_data = await request.json()
        except JSONDecodeError:
            json_data = None

        new_request: RequestData = RequestData(
            request_id=new_id,
            headers=request.headers,
            url = str(request.url),
            cookies = request.cookies,
            data = json_data if json_data is not None else {}
        )
        level_obj.request_data.append(new_request)

        if len(level_obj.request_data) > 3:
            level_obj.request_data = level_obj.request_data[1:] # Make sure that it does not get longer than 3

        self.updated_at = datetime.datetime.now(datetime.UTC)
        await self.save()

    async def get_last_requests(self, level: str, last=3):
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            return []

        to_return = level_obj.request_data[-last:]

        return [str(x) for x in to_return]

    async def get_last_hint(self, level: str) -> str:
        level_obj = self.level_data.get(level, None)
        if level_obj is None:
            raise exceptions.LevelNotFound(level)
        return level_obj.hint_data[-1].hint_text
