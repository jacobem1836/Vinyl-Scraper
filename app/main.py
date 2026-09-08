import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.auth import AuthRedirect, auth_redirect_response
from app.config import settings
from app.database import engine
from app.migrations import run_migrations
from app.routers.auth import auth_router
from app.routers.public import public_router
from app.routers.wishlist import api_router, web_router
from app.scheduler import scheduler, setup_scheduler
from app.templating import templates

SESSION_MAX_AGE = 60 * 60 * 24 * 30

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    ),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await asyncio.to_thread(run_migrations, engine)
    setup_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="CRATE", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for k, v in SECURITY_HEADERS.items():
            response.headers.setdefault(k, v)
        if settings.is_production:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="crate_session",
    max_age=SESSION_MAX_AGE,
    same_site="lax",
    https_only=settings.is_production,
)


def _wants_html(request: Request) -> bool:
    return not request.url.path.startswith("/api/") and "text/html" in request.headers.get("accept", "")


@app.exception_handler(AuthRedirect)
async def _auth_redirect(request: Request, exc: AuthRedirect):
    return auth_redirect_response(exc.next_path)


@app.exception_handler(HTTPException)
async def _http_error(request: Request, exc: HTTPException):
    if _wants_html(request):
        return templates.TemplateResponse(request, "error.html", {"status": exc.status_code, "message": exc.detail}, status_code=exc.status_code)
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None))


@app.exception_handler(Exception)
async def _server_error(request: Request, exc: Exception):
    print(f"[error] {request.method} {request.url.path}: {exc!r}")
    if _wants_html(request):
        return templates.TemplateResponse(request, "error.html", {"status": 500, "message": "Something went wrong on our side. Please try again."}, status_code=500)
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(web_router)
app.include_router(api_router)
