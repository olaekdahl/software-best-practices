# DIP: depend on abstractions, not concretes
# Talking points:
# - Service depends on a Logger abstraction, not a concrete class.
# - Swap ConsoleLogger for another impl without editing Service.
# - Improves testability and flexibility.
#
# Key idea:
# - The Service accepts a Logger abstraction (Protocol), not a specific class.
#   That lets you swap ConsoleLogger for a FileLogger, NullLogger, or a test double
#   without changing Service. Improves testability and flexibility.
from typing import Protocol


class Logger(Protocol):
    def info(self, msg: str) -> None: ...


class ConsoleLogger:
    def info(self, msg: str) -> None:
        print(f"[INFO] {msg}")


class Service:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def do_work(self) -> None:
        # Business logic calls into the abstraction; no concrete coupling here
        self.logger.info("Service started")
        # ... work here ...
        self.logger.info("Service finished")


if __name__ == "__main__":
    svc = Service(ConsoleLogger())
    svc.do_work()
