import hashlib
import hmac
import secrets
import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

SECRET_SALT = os.environ.get("DEVICE_SECRET_SALT", "krishinidhi_smart_plant_salt_2026")
JWT_SECRET = os.environ.get("JWT_SECRET", "super_secret_jwt_key_change_in_prod")
JWT_ALGORITHM = "HS256"

def hash_api_key(api_key: str) -> str:
    """Computes a cryptographically secure SHA-256 hash of the device API key."""
    return hashlib.sha256(f"{SECRET_SALT}:{api_key}".encode("utf-8")).hexdigest()

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Constant-time comparison of hashed API key to prevent timing attacks."""
    computed_hash = hash_api_key(provided_key)
    return hmac.compare_digest(computed_hash, stored_hash)

def generate_device_api_key(prefix: str = "spk") -> str:
    """Generates a secure, 32-byte URL-safe device API key."""
    random_part = secrets.token_urlsafe(24)
    return f"{prefix}_{random_part}"

def get_device_auth(
    x_device_key: Optional[str] = Header(None, alias="X-Device-Key"),
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """
    Extracts device key from either 'X-Device-Key' header or 'Authorization: Bearer <key>'.
    Returns None if missing.
    """
    if x_device_key:
        return x_device_key.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None
