import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    aws_region: str
    db_url: str
    queue_url: str


def load_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        db_url=os.getenv("DB_URL", ""),
        queue_url=os.getenv("QUEUE_URL", ""),
    )

