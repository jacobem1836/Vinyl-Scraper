"""Operator commands. Run from the repo root with the app's environment loaded:

    python -m app.cli invite someone@example.com     # allow a waitlist address to sign up
    python -m app.cli waitlist                         # list waitlist entries
    python -m app.cli set-password you@example.com     # set/reset a password interactively
    python -m app.cli verify you@example.com           # mark an email verified
    python -m app.cli migrate                          # run schema migrations only
"""
import getpass
import sys
from datetime import datetime

from app.auth import hash_password, password_problem
from app.database import SessionLocal, engine
from app.migrations import run_migrations
from app.models import User, WaitlistEntry


def _norm(email: str) -> str:
    return email.strip().lower()


def cmd_invite(email: str) -> None:
    email = _norm(email)
    with SessionLocal() as db:
        entry = db.query(WaitlistEntry).filter_by(email=email).first()
        if entry is None:
            entry = WaitlistEntry(email=email)
            db.add(entry)
        entry.invited_at = entry.invited_at or datetime.utcnow()
        db.commit()
    print(f"invited {email}: they can now sign up at /signup with that address")


def cmd_waitlist() -> None:
    with SessionLocal() as db:
        for e in db.query(WaitlistEntry).order_by(WaitlistEntry.created_at).all():
            state = "invited" if e.invited_at else "waiting"
            print(f"{e.created_at:%Y-%m-%d}  {state:8}  {e.email}")


def cmd_set_password(email: str) -> None:
    email = _norm(email)
    pw = getpass.getpass("New password: ")
    problem = password_problem(pw)
    if problem:
        sys.exit(problem)
    with SessionLocal() as db:
        user = db.query(User).filter_by(email=email).first()
        if user is None:
            sys.exit(f"no user {email}")
        user.password_hash = hash_password(pw)
        db.commit()
    print(f"password updated for {email}")


def cmd_verify(email: str) -> None:
    email = _norm(email)
    with SessionLocal() as db:
        user = db.query(User).filter_by(email=email).first()
        if user is None:
            sys.exit(f"no user {email}")
        user.email_verified_at = user.email_verified_at or datetime.utcnow()
        db.commit()
    print(f"{email} marked verified")


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    run_migrations(engine)
    if cmd == "migrate":
        return
    if cmd == "invite" and args:
        return cmd_invite(args[0])
    if cmd == "waitlist":
        return cmd_waitlist()
    if cmd == "set-password" and args:
        return cmd_set_password(args[0])
    if cmd == "verify" and args:
        return cmd_verify(args[0])
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
