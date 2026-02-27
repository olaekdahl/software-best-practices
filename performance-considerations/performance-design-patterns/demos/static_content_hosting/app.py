from __future__ import annotations

import time
from dataclasses import dataclass

@dataclass(frozen=True)
class Response:
    status: int
    body: str
    headers: dict[str, str]

STATIC_ASSETS = {
    "/logo.svg": "<svg>...</svg>",
    "/app.css": "body{font-family:sans-serif}",
}

def static_host(path: str) -> Response:
    body = STATIC_ASSETS.get(path)
    if body is None:
        return Response(404, "not found", {})
    # Pretend this is served from an optimized static tier (CDN) with caching headers
    return Response(200, body, {"cache-control": "public, max-age=31536000"})

def app_backend(path: str) -> Response:
    # Dynamic business logic only
    if path == "/api/time":
        return Response(200, str(time.time()), {"content-type": "text/plain"})
    return Response(404, "not found", {})

def main() -> None:
    print("Static asset via static host:", static_host("/app.css"))
    print("Dynamic request via app backend:", app_backend("/api/time"))
    print("Static content offloaded to a specialized tier reduces load on the app.")

if __name__ == "__main__":
    main()
