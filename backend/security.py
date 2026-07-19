"""Password and opaque session-token helpers with no extra auth dependency."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt$16384$8$1${base64.b64encode(salt).decode()}${base64.b64encode(derived).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, n, r, p, encoded_salt, encoded_digest = stored_hash.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=base64.b64decode(encoded_salt),
            n=int(n), r=int(r), p=int(p),
        )
        return hmac.compare_digest(actual, base64.b64decode(encoded_digest))
    except (ValueError, TypeError):
        return False


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def session_expiry() -> str:
    return (datetime.now(UTC) + timedelta(days=7)).isoformat()
