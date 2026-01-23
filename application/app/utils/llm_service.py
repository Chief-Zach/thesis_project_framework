import os

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from anthropic import DefaultAioHttpClient
from ollama import Client

from dotenv import load_dotenv
from typing import Union, List
import asyncio

from abc import ABC, abstractmethod

load_dotenv()

class LLMConnector(ABC):
    def __init__(self) -> None:
        self.client: Union[AsyncAnthropic, AsyncOpenAI]

    @abstractmethod
    async def get_hint(self, prompt, past_queries: Union[List[str], None]) -> str:
        raise NotImplementedError

class ChatGPTConnector(LLMConnector):
    def __init__(self):
        super().__init__()
        self.client = AsyncOpenAI(
            api_key=os.getenv("CHAT_KEY"),
        )

    async def get_hint(self, prompt, past_queries: Union[List[str], None]=None):
        input_data = [{"role": "system", "content": prompt}]
        if past_queries is not None:
            for query in past_queries:
                input_data.append({"role": "user", "content": query})

        response = await self.client.responses.create(
            max_output_tokens=4096,
            model="gpt-5-nano",
            input = input_data
        )
        text = response.output_text

        return text

class OllamaConnector(LLMConnector):
    def __init__(self, ollama_port, ollama_model):
        super().__init__()

        self.client = Client(host=f"http://localhost:{ollama_port}")
        self.ollama_model = ollama_model
        self.ollama_lock = asyncio.Lock()

    async def _get_hint(self, input_data):
        async with self.ollama_lock:
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.ollama_model,
                messages=input_data,
                keep_alive='5m',
                stream=False
            )

        return response
    async def get_hint(self, prompt, past_queries: Union[List[str], None]) -> str:
        input_data = [{"role": "system", "content": prompt}]
        if past_queries is not None:
            for query in past_queries:
                input_data.append({"role": "user", "content": query})

        response = await self._get_hint(input_data)

        text = response.message.content

        return text

class ClaudeConnector(LLMConnector):
    def __init__(self):
        super().__init__()
        self.client = AsyncAnthropic(
            http_client=DefaultAioHttpClient(),
            api_key=os.getenv("CLAUDE_KEY")
        )

    async def get_hint(self, prompt, past_queries: Union[List[str], None]=None):
        input_data = []
        if past_queries is not None:
            for query in past_queries:
                input_data.append({"role": "user", "content": str(query)})

        response = await self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=[
                {
                    "type": "text",
                    "text": f"{prompt}",
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=input_data,
        )

        text = response.content

        return text