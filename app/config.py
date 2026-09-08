from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings

DEV_SECRET = "dev-insecure-change-me"


class Settings(BaseSettings):
    env: str = "development"  # "development" | "production"
    database_url: str = "sqlite:///./vinyl.db"
    secret_key: str = DEV_SECRET  # signs session cookies, CSRF tokens, email links
    app_url: str = "http://localhost:8000"  # absolute base URL used in emails

    discogs_token: Optional[str] = None
    ebay_app_id: Optional[str] = None
    ebay_cert_id: Optional[str] = None

    resend_api_key: Optional[str] = None
    resend_from: Optional[str] = None  # e.g. "CRATE <alerts@example.com>"

    scan_interval_hours: int = 6
    scan_min_interval_minutes: int = 10  # per-user manual rescan throttle
    shipping_estimate_aud: float = 30.0  # fallback landed shipping when origin is unknown
    relevance_threshold: float = 70.0  # listings scoring below this are hidden
    notify_cooldown_hours: int = 24  # minimum gap between digest emails per item

    signup_mode: str = "invite"  # "invite" (waitlist + invite) | "open"
    legacy_owner_email: Optional[str] = None  # pre-auth wishlist rows are assigned to this user on migrate

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"

    @model_validator(mode="after")
    def _check_production(self):
        if self.is_production:
            if self.secret_key == DEV_SECRET or len(self.secret_key) < 32:
                raise ValueError("SECRET_KEY must be set to a random value of at least 32 characters in production")
            if not self.app_url.startswith("https://"):
                raise ValueError("APP_URL must be an https:// URL in production")
        return self


settings = Settings()
