from __future__ import annotations
import base64
import hashlib
import hmac
import secrets
from fastapi import HTTPException, status


def verify_code_challenge(code_verifier: str, stored_challenge: str) -> bool:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")

    if not hmac.compare_digest(computed, stored_challenge):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PKCE verification failed. Code verifier mismatch.",
        )
    return True


def generate_state() -> str:

    return secrets.token_hex(32)
