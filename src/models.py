from pydantic import BaseModel, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Notification(BaseModel):
    urls: AnyUrl | list[AnyUrl]
    title: str = 'Alert'
    body: str
    attachments: list | None = None

class Settings(BaseSettings):
    broker: str
    port: int = 1883
    user: str = None
    password: str = None
    base_topic: str

    model_config = SettingsConfigDict(
        env_prefix='NOTIFIER_',
        env_file_encoding='utf-8'
    )