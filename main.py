import json
from typing import AsyncGenerator
from fastapi.responses import FileResponse
import requests
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import aiofiles
import os.path
import asyncio

from sse_starlette import EventSourceResponse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    discord_webhook_url: str | None = None
    title: str = "Claude Code work completed."
    message_template: str = "prompt: {prompt}"
    show_prompt: bool = True


class StopEvent(BaseModel):
    transcript_path: str | None = None


class NotificationManager:
    def __init__(self):
        self.clients: list[asyncio.Queue] = []

    async def add_client(self) -> AsyncGenerator[dict, None]:
        queue: asyncio.Queue = asyncio.Queue()
        self.clients.append(queue)
        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self.clients.remove(queue)

    async def notify_all(self, title: str, message: str | None):
        notification_data = {
            "title": title,
            "message": message,
        }

        for client in self.clients:
            await client.put(notification_data)


settings = Settings()
notification_manager = NotificationManager()

app = FastAPI()


async def extract_prompt(event: StopEvent | None) -> str | None:
    if (
        settings.show_prompt
        and event
        and event.transcript_path
        and os.path.exists(event.transcript_path)
    ):
        try:
            last_message = None
            async with aiofiles.open(
                event.transcript_path, mode="r", encoding="utf-8"
            ) as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    log = json.loads(line)
                    if isinstance(log, dict):
                        if log.get("type") == "user" and "toolUseResult" not in log:
                            message = log.get("message", {}).get("content")
                            if isinstance(message, str):
                                last_message = message
            return last_message
        except Exception:
            pass
    return None


@app.post("/notify")
async def notify(event: StopEvent | None = None):
    prompt = await extract_prompt(event)

    title = settings.title
    message = settings.message_template.format(prompt=prompt) if prompt else None

    await notification_manager.notify_all(title, message)

    if settings.discord_webhook_url:
        content = f"{title}\n{message}" if message else title
        requests.post(
            settings.discord_webhook_url,
            json={"content": content},
        )
    return {"status": "OK"}


@app.get("/")
@app.get("/index.html")
async def get_index():
    return FileResponse("index.html")


@app.get("/notifications")
async def get_notifications():
    async def event_generator():
        async for content in notification_manager.add_client():
            yield {
                "event": "message",
                "data": json.dumps(content, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())
