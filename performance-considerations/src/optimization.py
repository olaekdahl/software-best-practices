from __future__ import annotations

import functools
import time
from pathlib import Path


@functools.lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_demo():
    print("-- caching (lru_cache) --")
    t0 = time.perf_counter()
    a = fib(32)
    t1 = time.perf_counter()
    b = fib(32)  # cached
    t2 = time.perf_counter()
    print(f"fib(32)={a}, first={t1-t0:.4f}s, second(cached)={t2-t1:.6f}s")


class LazyFile:
    def __init__(self, path: Path):
        self._path = path
        self._lines: list[str] | None = None

    @property
    def lines(self) -> list[str]:
        if self._lines is None:
            # Lazy load
            self._lines = self._path.read_text(encoding="utf-8").splitlines()
        return self._lines


def lazy_loading_demo():
    print("-- lazy loading --")
    path = Path("/tmp/lazy.txt")
    path.write_text("".join(f"line {i}\n" for i in range(100_000)), encoding="utf-8")
    lf = LazyFile(path)
    t0 = time.perf_counter()
    # No load yet
    t1 = time.perf_counter()
    _ = lf.lines  # triggers load
    t2 = time.perf_counter()
    path.unlink()
    print(f"Access property: before load={t1-t0:.6f}s, after first access (load)={t2-t1:.4f}s")


def main():
    fib_demo()
    lazy_loading_demo()


if __name__ == "__main__":
    main()
