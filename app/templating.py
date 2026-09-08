from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.auth import csrf_token
from app.config import settings


def _globals(request: Request) -> dict:
    return {
        "csrf_token": lambda: csrf_token(request),
        "app_url": settings.app_url,
        "signup_open": settings.signup_mode == "open",
    }


templates = Jinja2Templates(directory="templates", context_processors=[_globals])
