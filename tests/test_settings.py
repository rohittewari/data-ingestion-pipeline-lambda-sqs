from src.config.settings import load_settings


def test_load_settings_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("DB_URL", raising=False)
    monkeypatch.delenv("QUEUE_URL", raising=False)

    settings = load_settings()

    assert settings.app_env == "dev"
    assert settings.log_level == "INFO"
    assert settings.aws_region == "us-east-1"
    assert settings.db_url == ""
    assert settings.queue_url == ""

