from __future__ import annotations

import gzip
import json
import time
from dataclasses import dataclass

@dataclass
class Response:
    status: int
    body: bytes
    headers: dict[str, str]

def backend() -> dict:
    # Business logic returns a Python object
    return {"message": "hello", "ts": time.time(), "items": list(range(50))}

def gateway_offload() -> Response:
    # Offload serialization + compression to the gateway
    obj = backend()
    raw = json.dumps(obj).encode()
    gz = gzip.compress(raw)
    return Response(
        status=200,
        body=gz,
        headers={"content-type": "application/json", "content-encoding": "gzip", "raw-bytes": str(len(raw))}
    )

def main() -> None:
    resp = gateway_offload()
    print("Gateway returned headers:", resp.headers)
    print("Compressed bytes:", len(resp.body), "raw bytes:", resp.headers["raw-bytes"])

if __name__ == "__main__":
    main()
