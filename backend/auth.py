"""Shared-access-code authentication for the /api/ask endpoint.

A single access code (ACCESS_CODE) unlocks a signed, self-verifying session
token, no database, nothing stored server-side beyond the code and the
signing secret. /api/login issues the token, require_session checks it.

Login attempts are rate-limited per IP, in memory, this is the control that
actually matters here, not the length of the code.
"""

import hashlib
import hmac
import logging
import os
import time
from collections import defaultdict, deque

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger("ukask")

ACCESS_CODE = os.getenv("ACCESS_CODE")
SESSION_SECRET = os.getenv("SESSION_SECRET")
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

LOGIN_RATE_LIMIT = 5          # attempts
LOGIN_RATE_WINDOW = 15 * 60   # per 15 minutes, per IP

router = APIRouter()

# ip -> deque of attempt timestamps, pruned on every check. Fine for a
# single-process deployment, this resets on restart and doesn't share state
# across workers, which is an acceptable tradeoff at this scale, not one
# that needs redis.
_login_attempts: dict[str, deque[float]] = defaultdict(deque)


def check_auth_config():
    """Fail startup loudly if the secrets aren't set, rather than letting
    every login attempt fail confusingly later."""
    if not ACCESS_CODE or not SESSION_SECRET:
        raise RuntimeError(
            "ACCESS_CODE and SESSION_SECRET must be set (in .env locally, or "
            "as repository secrets when deployed) before the API can start."
        )


def _make_token() -> str:
    expiry = int(time.time()) + SESSION_TTL_SECONDS
    payload = str(expiry)
    signature = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def _verify_token(token: str) -> bool:
    try:
        payload, signature = token.split(".")
        expected = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected) and int(payload) > time.time()
    except (ValueError, AttributeError):
        return False


def _rate_limited(ip: str) -> bool:
    now = time.time()
    attempts = _login_attempts[ip]
    while attempts and now - attempts[0] > LOGIN_RATE_WINDOW:
        attempts.popleft()
    return len(attempts) >= LOGIN_RATE_LIMIT


def _record_attempt(ip: str):
    _login_attempts[ip].append(time.time())


class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str


@router.post("/api/login", response_model=LoginResponse)
def login(body: LoginRequest, request: Request):
    ip = request.client.host if request.client else "unknown"

    if _rate_limited(ip):
        logger.warning("login rate limit hit for %s", ip)
        raise HTTPException(
            status_code=429,
            detail="Too many attempts, please wait a few minutes and try again.",
        )

    _record_attempt(ip)

    if not hmac.compare_digest(body.code, ACCESS_CODE):
        raise HTTPException(status_code=401, detail="Invalid code")

    return LoginResponse(token=_make_token())


def require_session(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session")
    token = authorization.removeprefix("Bearer ")
    if not _verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired session")