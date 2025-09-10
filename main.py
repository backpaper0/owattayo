import json
from typing import AsyncGenerator
from fastapi.staticfiles import StaticFiles
import requests
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import asyncio

from sse_starlette import EventSourceResponse


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    discord_webhook_url: str | None = None
    default_title: str = "Notification"


class Notification(BaseModel):
    title: str
    body: str | None = None
    url: str | None = None


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

    async def notify_all(
        self,
        title: str,
        body: str | None,
        url: str | None = None,
    ):
        notification_data = {
            "title": title,
            "body": body,
            "url": url,
        }

        for client in self.clients:
            await client.put(notification_data)


settings = Settings()
notification_manager = NotificationManager()

app = FastAPI()


@app.post("/notify")
async def notify(event: Notification | None = None):
    title = event.title if event else settings.default_title
    body = event.body if event else None
    url = event.url if event else None

    await notification_manager.notify_all(title, body, url)

    if settings.discord_webhook_url:
        content = title
        content += f"\n{body}" if body else ""
        content += f"\n{url}" if url else ""
        requests.post(
            settings.discord_webhook_url,
            json={"content": content},
        )
    return {"status": "OK"}


@app.get("/notifications")
async def get_notifications():
    async def event_generator():
        async for content in notification_manager.add_client():
            yield {
                "event": "message",
                "data": json.dumps(content, ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


app.mount("/", StaticFiles(directory="static", html=True), name="static")
