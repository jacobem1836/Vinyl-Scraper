"""Auth routes: /login, /signup, /logout.

Mirroring patterns from app/routers/wishlist.py.
Session cookie name: crate_session (set by SessionMiddleware in main.py).
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.database import get_db
from app.models import User

auth_router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")

MIN_PASSWORD_LEN = 8


def _safe_next(next_param: str | None) -> str:
    """Whitelist next= to relative paths only. Prevents open-redirect.

    T-29-07: External URLs and protocol-relative //host paths are rejected.
    """
    if not next_param:
        return "/"
    if not next_param.startswith("/") or next_param.startswith("//"):
        return "/"
    return next_param


@auth_router.get("/login")
async def login_page(request: Request, next: str = "", error: str = ""):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "next": next, "error": error, "email": ""},
    )


@auth_router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form(""),
    db: Session = Depends(get_db),
):
    email_norm = email.strip().lower()
    user = db.query(User).filter_by(email=email_norm).first()
    # T-29-08: Generic message hides whether email or password was wrong.
    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "next": next,
                "error": "Invalid email or password.",
                "email": email_norm,
            },
            status_code=200,
        )
    request.session["user_id"] = user.id
    return RedirectResponse(url=_safe_next(next), status_code=303)


@auth_router.get("/signup")
async def signup_page(request: Request, next: str = "", error: str = ""):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "next": next, "error": error, "email": ""},
    )


@auth_router.post("/signup")
async def signup_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form(""),
    db: Session = Depends(get_db),
):
    email_norm = email.strip().lower()

    def _err(msg: str):
        # T-29-09: Only email is round-tripped; password is never re-rendered.
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "next": next, "error": msg, "email": email_norm},
            status_code=200,
        )

    if "@" not in email_norm or "." not in email_norm:
        return _err("Please enter a valid email address.")
    if len(password) < MIN_PASSWORD_LEN:
        return _err(f"Password must be at least {MIN_PASSWORD_LEN} characters.")

    existing = db.query(User).filter_by(email=email_norm).first()
    if existing is not None:
        return _err("An account with that email already exists.")

    user = User(email=email_norm, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        return _err("An account with that email already exists.")
    request.session["user_id"] = user.id
    return RedirectResponse(url=_safe_next(next), status_code=303)


@auth_router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
