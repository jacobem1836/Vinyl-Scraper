from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./vinyl.db"
    api_key: str = "change-me-please"
    discogs_token: Optional[str] = None
    ebay_app_id: Optional[str] = None    # eBay App ID (Client ID) for Browse API
    ebay_cert_id: Optional[str] = None   # eBay Cert ID (Client Secret) for Browse API
    resend_api_key: Optional[str] = None
    resend_from: Optional[str] = None   # e.g. "Crate <alerts@yourdomain.com>"
    notify_email: Optional[str] = None
    scan_interval_hours: int = 6
    shipping_estimate_usd: float = 20.0  # flat shipping estimate to Australia, added to displayed prices
    notify_below_pct_default: float = 20.0  # global default notification threshold (% below typical)

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}

settings = Settings()
