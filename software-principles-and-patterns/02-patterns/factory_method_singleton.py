# Factory Method / Singleton demo
# Talking points:
# - Factory centralizes which logger to build (creation logic).
# - Simple singleton cache shares one instance per kind.
# - Caveats: hidden global state; clear cache in tests if needed.
#
# Intent
# - Factory Method: centralize object creation decisions (which concrete to build).
# - Singleton: keep a single shared instance per kind (cached in the factory).
#
# When to use
# - Factory: callers shouldn't know which logger to instantiate (decide by config).
# - Singleton: the cost/state favors reuse (idempotent, stateless, or shared sink).
#
# Trade-offs
# - Singleton can become hidden global state; prefer explicit dependency injection.
# - Consider lifecycle (close/flush) and tests (reset cache between tests if needed).
# - For multi-process apps, this is per-process, not cluster-wide.
from __future__ import annotations
from typing import Dict, Protocol


class Logger(Protocol):
    def log(self, msg: str) -> None: ...


class ConsoleLogger:
    def log(self, msg: str) -> None:
        print(f"[Console] {msg}")


class JsonLogger:
    def log(self, msg: str) -> None:
        import json
        print(json.dumps({"message": msg}))


class LoggerFactory:
    _singletons: Dict[str, Logger] = {}

    @classmethod
    def get(cls, kind: str) -> Logger:
        # Factory Method decides which concrete to create
        # and caches it (simple Singleton registry by key)
        if kind not in cls._singletons:
            if kind == "console":
                cls._singletons[kind] = ConsoleLogger()
            elif kind == "json":
                cls._singletons[kind] = JsonLogger()
            else:
                raise ValueError(f"unknown logger kind: {kind}")
        return cls._singletons[kind]


if __name__ == "__main__":
    # In tests you might want to clear LoggerFactory._singletons = {} between cases
    a = LoggerFactory.get("console")
    b = LoggerFactory.get("console")
    print("Singleton?", a is b)
    a.log("hello from factory method")
    LoggerFactory.get("json").log("hello as json")
