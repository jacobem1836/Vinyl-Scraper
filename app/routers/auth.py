"""Account routes: signup (invite-gated), login, logout, email verification, password reset, account page."""
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import (
    hash_password, login_session, make_reset_token, make_verify_token, mark_verified, password_problem,
    read_reset_token, read_verify_token, require_auth, require_csrf, throttle, verify_password,
)
from app.config import settings
from app.database import get_db
from app.models import User, WaitlistEntry
from app.services import mailer
from app.templating import templates

auth_router = APIRouter(tags=["auth"])


def _norm(email: str) -> str:
    return email.strip().lower()


def _safe_next(next_param: str | None) -> str:
    """Relative paths only; blocks open redirects and protocol-relative //host."""
    if not next_param or not next_param.startswith("/") or next_param.startswith("//"):
        return "/"
    return next_param


def _invited(db: Session, email: str) -> bool:
    if settings.signup_mode == "open":
        return True
    entry = db.query(WaitlistEntry).filter_by(email=email).first()
    return bool(entry and entry.invited_at)


async def send_verification(user: User) -> bool:
    link = f"{settings.app_url}/verify/{make_verify_token(user)}"
    html = templates.env.get_template("email/verify.html").render(link=link, app_url=settings.app_url)
    return await mailer.send_email(user.email, "Confirm your CRATE email", html)


# --- signup / login / logout -------------------------------------------------------

@auth_router.get("/signup")
async def signup_page(request: Request, next: str = ""):
    return templates.TemplateResponse(request, "signup.html", {"next": next, "error": "", "email": "", "invite_only": settings.signup_mode != "open"})


@auth_router.post("/signup", dependencies=[Depends(require_csrf)])
async def signup_submit(request: Request, email: str = Form(...), password: str = Form(...), next: str = Form(""), db: Session = Depends(get_db)):
    throttle(request, "signup", limit=5, window_seconds=3600)
    email_norm = _norm(email)

    def _err(msg: str):
        return templates.TemplateResponse(request, "signup.html", {"next": next, "error": msg, "email": email_norm, "invite_only": settings.signup_mode != "open"})

    if "@" not in email_norm or "." not in email_norm.split("@")[-1] or len(email_norm) > 254:
        return _err("Please enter a valid email address.")
    problem = password_problem(password)
    if problem:
        return _err(problem)
    if not _invited(db, email_norm):
        return _err("CRATE is invite-only right now. Join the waitlist on the home page and we'll email you when a spot opens.")

    user = User(email=email_norm, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _err("An account with that email already exists. Try signing in instead.")
    db.refresh(user)
    await send_verification(user)
    login_session(request, user)
    return RedirectResponse(url="/?toast=Welcome+to+CRATE.+Check+your+email+to+confirm+your+address.", status_code=303)


@auth_router.get("/login")
async def login_page(request: Request, next: str = ""):
    return templates.TemplateResponse(request, "login.html", {"next": next, "error": "", "email": ""})


@auth_router.post("/login", dependencies=[Depends(require_csrf)])
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...), next: str = Form(""), db: Session = Depends(get_db)):
    email_norm = _norm(email)
    throttle(request, "login-ip", limit=20, window_seconds=900)
    throttle(request, "login-email", limit=8, window_seconds=900, extra_key=email_norm)
    user = db.query(User).filter_by(email=email_norm).first()
    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html", {"next": next, "error": "Invalid email or password.", "email": email_norm})
    login_session(request, user)
    return RedirectResponse(url=_safe_next(next), status_code=303)


@auth_router.post("/logout", dependencies=[Depends(require_csrf)])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# --- email verification --------------------------------------------------------------

@auth_router.get("/verify/{token}")
async def verify_email(token: str, request: Request, db: Session = Depends(get_db)):
    data = read_verify_token(token)
    user = db.get(User, data["uid"]) if data else None
    if user is None or user.email != data.get("email"):
        return templates.TemplateResponse(request, "error.html", {"status": 400, "message": "That confirmation link is invalid or has expired. Sign in and request a new one from your account page."}, status_code=400)
    mark_verified(user)
    db.commit()
    return RedirectResponse(url="/?toast=Email+confirmed.+Deal+alerts+are+on.", status_code=303)


@auth_router.post("/resend-verification", dependencies=[Depends(require_csrf)])
async def resend_verification(request: Request, user: User = Depends(require_auth)):
    throttle(request, "resend", limit=3, window_seconds=3600, extra_key=str(user.id))
    if not user.is_verified:
        await send_verification(user)
    return RedirectResponse(url="/account?toast=Confirmation+email+sent", status_code=303)


# --- password reset ---------------------------------------------------------------------

@auth_router.get("/forgot-password")
async def forgot_page(request: Request):
    return templates.TemplateResponse(request, "forgot.html", {"sent": False})


@auth_router.post("/forgot-password", dependencies=[Depends(require_csrf)])
async def forgot_submit(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    throttle(request, "forgot", limit=5, window_seconds=3600)
    user = db.query(User).filter_by(email=_norm(email)).first()
    if user is not None:
        link = f"{settings.app_url}/reset-password/{make_reset_token(user)}"
        html = templates.env.get_template("email/reset.html").render(link=link, app_url=settings.app_url)
        await mailer.send_email(user.email, "Reset your CRATE password", html)
    # Same response whether or not the address exists.
    return templates.TemplateResponse(request, "forgot.html", {"sent": True})


@auth_router.get("/reset-password/{token}")
async def reset_page(token: str, request: Request, db: Session = Depends(get_db)):
    if read_reset_token(token, db) is None:
        return templates.TemplateResponse(request, "error.html", {"status": 400, "message": "That reset link is invalid or has expired. Request a new one."}, status_code=400)
    return templates.TemplateResponse(request, "reset.html", {"token": token, "error": ""})


@auth_router.post("/reset-password/{token}", dependencies=[Depends(require_csrf)])
async def reset_submit(token: str, request: Request, password: str = Form(...), db: Session = Depends(get_db)):
    throttle(request, "reset", limit=10, window_seconds=3600)
    user = read_reset_token(token, db)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")
    problem = password_problem(password)
    if problem:
        return templates.TemplateResponse(request, "reset.html", {"token": token, "error": problem})
    user.password_hash = hash_password(password)
    mark_verified(user)  # they proved control of the mailbox
    db.commit()
    login_session(request, user)
    return RedirectResponse(url="/?toast=Password+updated", status_code=303)


# --- account -------------------------------------------------------------------------------

@auth_router.get("/account")
async def account_page(request: Request, user: User = Depends(require_auth)):
    return templates.TemplateResponse(request, "account.html", {"user": user, "error": "", "mail_configured": mailer.is_configured()})


@auth_router.post("/account/password", dependencies=[Depends(require_csrf)])
async def change_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db), user: User = Depends(require_auth)):
    throttle(request, "change-pw", limit=10, window_seconds=3600, extra_key=str(user.id))
    if not verify_password(current_password, user.password_hash):
        return templates.TemplateResponse(request, "account.html", {"user": user, "error": "Current password is incorrect.", "mail_configured": mailer.is_configured()})
    problem = password_problem(new_password)
    if problem:
        return templates.TemplateResponse(request, "account.html", {"user": user, "error": problem, "mail_configured": mailer.is_configured()})
    user.password_hash = hash_password(new_password)
    db.commit()
    login_session(request, user)
    return RedirectResponse(url="/account?toast=Password+changed", status_code=303)


@auth_router.post("/account/delete", dependencies=[Depends(require_csrf)])
async def delete_account(request: Request, password: str = Form(...), db: Session = Depends(get_db), user: User = Depends(require_auth)):
    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "account.html", {"user": user, "error": "Password is incorrect; account not deleted.", "mail_configured": mailer.is_configured()})
    db.delete(user)  # cascades to wishlist items and listings
    db.commit()
    request.session.clear()
    return RedirectResponse(url="/?toast=Your+account+and+data+have+been+deleted", status_code=303)
