"""Auth helpers: bcrypt hashing, session-based current user, route guards.

Per D-03 in 29-CONTEXT.md: hand-rolled, no auth library.
"""
import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import quote

from app.database import get_db
from app.models import User

BCRYPT_ROUNDS = 12  # Standard work factor.


def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of `plaintext`. Output starts with $2b$."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(plaintext.encode("utf-8"), salt).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True iff plaintext matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def current_user(request: Request, db: Session) -> User | None:
    """Return the User for the current session, or None if unauthenticated."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter_by(id=user_id).first()


def require_auth(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: ensures request is authenticated.

    Returns the User row. If unauthenticated, raises an HTTPException whose
    handling is a 303 redirect to /login?next=<original_path>.

    Note: We raise AuthRedirect (a custom exception) rather than HTTPException
    because FastAPI dependencies cannot return RedirectResponse directly.
    An exception handler installed in main.py converts AuthRedirect to a 303 redirect.
    """
    user = current_user(request, db)
    if user is None:
        # Build the next= path: full path + query string.
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        raise AuthRedirect(next_path=next_path)
    return user


class AuthRedirect(Exception):
    """Raised by require_auth when the user is unauthenticated.

    Caught by an exception handler in app/main.py that issues a 303
    redirect to /login?next=<encoded_path>.
    """

    def __init__(self, next_path: str):
        self.next_path = next_path


def auth_redirect_response(next_path: str) -> RedirectResponse:
    """Build the redirect response used by the AuthRedirect handler."""
    return RedirectResponse(
        url=f"/login?next={quote(next_path, safe='')}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
