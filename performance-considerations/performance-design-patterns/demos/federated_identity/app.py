from __future__ import annotations

import base64
import hmac
import json
import time
from hashlib import sha256

# Very small 'token' format:
# token = base64(payload_json) + "." + base64(hmac(payload, shared_secret))

SECRET = b"shared-secret-between-idp-and-app"

def b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def b64d(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def issue_token(user: str, ttl_seconds: int = 60) -> str:
    payload = {"sub": user, "exp": int(time.time()) + ttl_seconds, "iss": "example-idp"}
    payload_b = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    sig = hmac.new(SECRET, payload_b, sha256).digest()
    return f"{b64e(payload_b)}.{b64e(sig)}"

def validate_token(token: str) -> dict:
    payload_s, sig_s = token.split(".")
    payload_b = b64d(payload_s)
    sig_b = b64d(sig_s)

    expected = hmac.new(SECRET, payload_b, sha256).digest()
    if not hmac.compare_digest(sig_b, expected):
        raise ValueError("bad signature")

    payload = json.loads(payload_b.decode())
    if payload["exp"] < int(time.time()):
        raise ValueError("token expired")

    return payload

def main() -> None:
    token = issue_token("alice", ttl_seconds=2)
    print("Client presents token (opaque to app):", token)
    claims = validate_token(token)
    print("App validates token locally and uses claims:", claims)

if __name__ == "__main__":
    main()
