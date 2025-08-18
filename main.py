import json
import requests
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import aiofiles
import os.path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    discord_webhook_url: str = ""
    completion_message: str = "Claude Code work completed."
    show_prompt: bool = True


class StopEvent(BaseModel):
    transcript_path: str | None = None


settings = Settings()

app = FastAPI()


async def extract_prompt(transcript_path: str | None) -> str | None:
    if transcript_path and os.path.exists(transcript_path):
        try:
            last_message = None
            async with aiofiles.open(transcript_path, mode="r", encoding="utf-8") as f:
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
async def notify(event: StopEvent):
    message = await extract_prompt(event.transcript_path)
    content = settings.completion_message
    if message:
        content = f"{content}\nprompt: {message}"
    requests.post(
        settings.discord_webhook_url,
        json={"content": content},
    )
    return {"status": "OK"}
