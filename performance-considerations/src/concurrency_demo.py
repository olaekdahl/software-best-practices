from __future__ import annotations

import concurrent.futures as cf
import math
import time


def io_task(duration: float = 0.2) -> float:
    time.sleep(duration)
    return duration


def cpu_task(n: int = 20_000) -> int:
    # Some CPU-heavy-ish work
    return sum(int(math.sqrt(i)) for i in range(n))


def io_sequential(m: int = 20) -> float:
    t0 = time.perf_counter()
    for _ in range(m):
        io_task()
    return time.perf_counter() - t0


def io_threads(m: int = 20) -> float:
    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor() as ex:
        list(ex.map(lambda _: io_task(), range(m)))
    return time.perf_counter() - t0


def cpu_threads(m: int = 8) -> float:
    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor() as ex:
        list(ex.map(cpu_task, [20_000] * m))
    return time.perf_counter() - t0


def cpu_processes(m: int = 8) -> float:
    t0 = time.perf_counter()
    with cf.ProcessPoolExecutor() as ex:
        list(ex.map(cpu_task, [20_000] * m))
    return time.perf_counter() - t0


def main():
    print("-- concurrency & parallelism --")
    t_seq = io_sequential()
    t_thr = io_threads()
    print(f"IO-bound: sequential={t_seq:.2f}s, threads={t_thr:.2f}s")

    t_thr_cpu = cpu_threads()
    t_proc_cpu = cpu_processes()
    print(f"CPU-bound: threads={t_thr_cpu:.2f}s, processes={t_proc_cpu:.2f}s")


if __name__ == "__main__":
    main()
