"""Simple password hashing (PBKDF2). No complexity rules — any non-empty string ok."""

from __future__ import annotations

import hashlib
import hmac
import secrets


def hash_password(password: str) -> str:
    """
    Return `salt_hex$hash_hex` for storage.

    Uses PBKDF2-HMAC-SHA256 — enough for a local multi-profile gate without
    pulling in bcrypt/passlib.
    """
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time compare of password against stored salt$hash."""
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(digest, expected)
