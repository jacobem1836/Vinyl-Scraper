"""Anonymous pages: landing with waitlist, privacy notice, health check."""
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import current_user, require_csrf, throttle
from app.database import get_db
from app.models import WaitlistEntry
from app.templating import templates

public_router = APIRouter(tags=["public"])


@public_router.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if user is not None:
        from app.routers.wishlist import dashboard
        return await dashboard(request, db, user)
    return templates.TemplateResponse(request, "landing.html", {"user": None, "joined": request.query_params.get("joined") == "1"})


@public_router.post("/waitlist", dependencies=[Depends(require_csrf)])
async def join_waitlist(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    throttle(request, "waitlist", limit=5, window_seconds=3600)
    email_norm = email.strip().lower()
    if "@" not in email_norm or "." not in email_norm.split("@")[-1] or len(email_norm) > 254:
        return templates.TemplateResponse(request, "landing.html", {"user": None, "joined": False, "error": "Please enter a valid email address."})
    db.add(WaitlistEntry(email=email_norm))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # already on the list; respond identically
    return RedirectResponse(url="/?joined=1#waitlist", status_code=303)


@public_router.get("/privacy")
async def privacy(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "privacy.html", {"user": current_user(request, db)})


@public_router.get("/api/health")
async def health():
    return {"status": "ok"}
