from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./vinyl.db"
    api_key: str = "change-me-please"
    discogs_token: Optional[str] = None
    smtp_host: str = "smtp.mail.me.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    notify_email: Optional[str] = None
    scan_interval_hours: int = 6
    shipping_estimate_usd: float = 20.0  # flat shipping estimate to Australia, added to displayed prices

    model_config = {"env_file": ".env", "case_sensitive": False}

settings = Settings()
