from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Request:
    path: str
    wants: str  # "read" or "write"

def read_backend(req: Request) -> str:
    return f"READ backend served {req.path}"

def write_backend(req: Request) -> str:
    return f"WRITE backend served {req.path}"

def gateway_route(req: Request) -> str:
    if req.wants == "read":
        return read_backend(req)
    return write_backend(req)

def main() -> None:
    print(gateway_route(Request("/orders/123", "read")))
    print(gateway_route(Request("/orders", "write")))
    print("Gateway routes by intent to optimize each backend independently.")

if __name__ == "__main__":
    main()
