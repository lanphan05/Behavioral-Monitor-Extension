"""Token hashing and secure generation helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets


TOKEN_PREFIX = "bm_"


def generate_api_token() -> str:
    """Return a high-entropy API token. Plaintext must not be stored."""
    return f"{TOKEN_PREFIX}{secrets.token_urlsafe(32)}"


def hash_api_token(plaintext: str) -> str:
    """Return the SHA-256 hex digest of a plaintext API token."""
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


def tokens_match(plaintext: str, token_hash: str) -> bool:
    """Constant-time comparison of plaintext token against a stored hash."""
    return hmac.compare_digest(hash_api_token(plaintext), token_hash)
