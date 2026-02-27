from __future__ import annotations

import hmac
import time
from hashlib import sha256

RESOURCE_SECRET = b"resource-secret"

def issue_valet_key(resource_id: str, ttl_seconds: int = 30) -> str:
    exp = int(time.time()) + ttl_seconds
    msg = f"{resource_id}:{exp}".encode()
    sig = hmac.new(RESOURCE_SECRET, msg, sha256).hexdigest()
    return f"{resource_id}:{exp}:{sig}"

def validate_valet_key(valet_key: str, want_resource_id: str) -> bool:
    resource_id, exp_s, sig = valet_key.split(":")
    if resource_id != want_resource_id:
        return False
    if int(exp_s) < int(time.time()):
        return False
    msg = f"{resource_id}:{exp_s}".encode()
    expected = hmac.new(RESOURCE_SECRET, msg, sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

def resource_download(resource_id: str, valet_key: str | None) -> str:
    if not valet_key or not validate_valet_key(valet_key, resource_id):
        return "403 forbidden"
    return f"200 ok (direct access) -> content for {resource_id}"

def main() -> None:
    key = issue_valet_key("file-123", ttl_seconds=2)
    print("Client receives scoped, time-limited valet key:", key)
    print(resource_download("file-123", key))

if __name__ == "__main__":
    main()
