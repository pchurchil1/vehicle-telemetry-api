import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings


ROLE_ADMIN = "admin"
ROLE_ENGINEER = "engineer"
ROLE_VIEWER = "viewer"
ROLES = {ROLE_ADMIN, ROLE_ENGINEER, ROLE_VIEWER}

ROLE_ORDER = {
    ROLE_VIEWER: 1,
    ROLE_ENGINEER: 2,
    ROLE_ADMIN: 3,
}

bearer_scheme = HTTPBearer(auto_error=False)


class AuthPrincipal:
    def __init__(self, username: str, role: str):
        self.username = username
        self.role = role


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_minutes)).timestamp()),
    }
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode()),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode()),
        ]
    )
    signature = hmac.new(
        settings.jwt_secret_key.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

    signing_input = f"{header_segment}.{payload_segment}"
    expected_signature = hmac.new(
        settings.jwt_secret_key.encode(),
        signing_input.encode(),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(_b64encode(expected_signature), signature_segment):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = json.loads(_b64decode(payload_segment))
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("exp") is None or int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Token expired")

    if payload.get("role") not in ROLES or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


def current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthPrincipal:
    if not settings.auth_enabled:
        return AuthPrincipal(username="dev", role=ROLE_ADMIN)

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    payload = decode_access_token(credentials.credentials)
    return AuthPrincipal(username=payload["sub"], role=payload["role"])


def require_roles(*allowed_roles: str):
    def dependency(principal: AuthPrincipal = Depends(current_principal)) -> AuthPrincipal:
        if principal.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal

    return dependency


def require_min_role(min_role: str):
    def dependency(principal: AuthPrincipal = Depends(current_principal)) -> AuthPrincipal:
        if ROLE_ORDER[principal.role] < ROLE_ORDER[min_role]:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal

    return dependency
