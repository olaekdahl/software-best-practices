from __future__ import annotations

import queue
import uuid

# Large payload store (blob store equivalent)
PAYLOAD_STORE: dict[str, bytes] = {}

def put_payload(data: bytes) -> str:
    key = uuid.uuid4().hex
    PAYLOAD_STORE[key] = data
    return key

def get_payload(key: str) -> bytes:
    return PAYLOAD_STORE[key]

def main() -> None:
    bus: queue.Queue[dict] = queue.Queue()

    # Producer stores payload out-of-band, puts only a pointer on the bus.
    big = b"x" * 1024 * 256  # 256KB
    pointer = put_payload(big)
    bus.put({"type": "image.uploaded", "payload_ref": pointer})
    print("Producer: sent message with claim check pointer:", pointer)

    # Consumer pulls small message; retrieves payload only if/when needed.
    msg = bus.get()
    data = get_payload(msg["payload_ref"])
    print("Consumer: retrieved payload length:", len(data))

if __name__ == "__main__":
    main()
