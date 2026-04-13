from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./vinyl.db"
    api_key: str = "change-me-please"
    discogs_token: Optional[str] = None
    ebay_app_id: Optional[str] = None    # eBay App ID (Client ID) for Browse API
    ebay_cert_id: Optional[str] = None   # eBay Cert ID (Client Secret) for Browse API
    smtp_host: str = "smtp.mail.me.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    notify_email: Optional[str] = None
    scan_interval_hours: int = 6
    shipping_estimate_usd: float = 20.0  # flat shipping estimate to Australia, added to displayed prices
    relevance_threshold_default: float = 70.0  # D-04: global min score to surface a listing
    notify_drop_pct_default: float = 20.0    # global pct price-drop threshold for notifications; per-item notify_drop_pct overrides
    notify_drop_usd_default: float = 5.0     # global usd price-drop threshold for notifications; per-item notify_drop_usd overrides
    notify_cooldown_hours: int = 24          # minimum hours between digest emails for the same item

    model_config = {"env_file": ".env", "case_sensitive": False}

settings = Settings()
