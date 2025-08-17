import requests
from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    discord_webhook_url: str = ""
    completion_message: str = "Claude Code work completed."


settings = Settings()

app = FastAPI()


@app.post("/notify")
def notify():
    requests.post(
        settings.discord_webhook_url,
        json={"content": settings.completion_message},
    )
    return {"status": "OK"}
