"""Auth primitives: password hashing, session user, route guards, CSRF, signed email tokens, rate limiting.

Sessions are Starlette signed cookies (see main.py). No auth library: the surface is small enough
that ~150 lines here is clearer than configuring one.
"""
import hmac
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime
from urllib.parse import quote

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

BCRYPT_ROUNDS = 12
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_BYTES = 72  # bcrypt input limit


# --- passwords -------------------------------------------------------------

def hash_password(plaintext: str) -> str:
    raw = plaintext.encode("utf-8")[:MAX_PASSWORD_BYTES]
    return bcrypt.hashpw(raw, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8")[:MAX_PASSWORD_BYTES], hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def password_problem(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LEN:
        return f"Password must be at least {MIN_PASSWORD_LEN} characters."
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        return "Password is too long (72 bytes max)."
    return None


# --- sessions ----------------------------------------------------------------

def login_session(request: Request, user: User) -> None:
    """Rotate the session on login so a pre-auth session cannot be fixated."""
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["csrf"] = secrets.token_urlsafe(32)


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


class AuthRedirect(Exception):
    """Raised by guards for browser routes; main.py turns it into a 303 to /login?next=..."""

    def __init__(self, next_path: str):
        self.next_path = next_path


def auth_redirect_response(next_path: str) -> RedirectResponse:
    return RedirectResponse(url=f"/login?next={quote(next_path, safe='')}", status_code=status.HTTP_303_SEE_OTHER)


def _next_path(request: Request) -> str:
    return f"{request.url.path}?{request.url.query}" if request.url.query else request.url.path


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    user = current_user(request, db)
    if user is None:
        raise AuthRedirect(next_path=_next_path(request))
    return user


def require_auth_json(request: Request, db: Session = Depends(get_db)) -> User:
    """Same guard for fetch()-driven endpoints: 401 JSON instead of a redirect."""
    user = current_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Not signed in")
    return user


# --- CSRF ----------------------------------------------------------------------

def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


async def require_csrf(request: Request) -> None:
    """Double-submit check against the session token. Forms send `csrf_token`; fetch() sends `X-CSRF-Token`."""
    expected = request.session.get("csrf")
    supplied = request.headers.get("x-csrf-token")
    if supplied is None and request.headers.get("content-type", "").startswith(
        ("application/x-www-form-urlencoded", "multipart/form-data")
    ):
        form = await request.form()
        supplied = form.get("csrf_token")
    if not expected or not supplied or not hmac.compare_digest(str(supplied), expected):
        raise HTTPException(status_code=403, detail="Invalid or missing CSRF token")


# --- signed email tokens (verification, password reset) ----------------------------

_serializer = URLSafeTimedSerializer(settings.secret_key)
VERIFY_MAX_AGE = 60 * 60 * 24 * 3
RESET_MAX_AGE = 60 * 60


def make_verify_token(user: User) -> str:
    return _serializer.dumps({"uid": user.id, "email": user.email}, salt="verify")


def read_verify_token(token: str) -> dict | None:
    try:
        return _serializer.loads(token, salt="verify", max_age=VERIFY_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def make_reset_token(user: User) -> str:
    # Binding to the current hash makes the link single-use: it stops validating once the password changes.
    return _serializer.dumps({"uid": user.id, "ph": user.password_hash[-16:]}, salt="reset")


def read_reset_token(token: str, db: Session) -> User | None:
    try:
        data = _serializer.loads(token, salt="reset", max_age=RESET_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    user = db.get(User, data.get("uid"))
    if user is None or not hmac.compare_digest(user.password_hash[-16:], data.get("ph", "")):
        return None
    return user


def mark_verified(user: User) -> None:
    if user.email_verified_at is None:
        user.email_verified_at = datetime.utcnow()


# --- rate limiting -----------------------------------------------------------------

class RateLimiter:
    """Sliding-window counter per key.

    ponytail: in-process only; correct because the app runs as a single machine (the scheduler
    requires that). Move to the database if it ever scales out.
    """

    def __init__(self) -> None:
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = time.monotonic()
        q = self._hits[key]
        while q and now - q[0] > window_seconds:
            q.popleft()
        if len(q) >= limit:
            return False
        q.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()


limiter = RateLimiter()


def client_ip(request: Request) -> str:
    # Fly's proxy sets Fly-Client-IP and strips any client-supplied copy; X-Forwarded-For's first hop is spoofable, so ignore it.
    return request.headers.get("fly-client-ip") or (request.client.host if request.client else "unknown")


def throttle(request: Request, bucket: str, limit: int, window_seconds: int, extra_key: str = "") -> None:
    key = f"{bucket}:{client_ip(request)}:{extra_key}"
    if not limiter.allow(key, limit, window_seconds):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again shortly.")
