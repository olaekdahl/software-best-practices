# gil_demo.py  (Python 3.11+)
# Shows: threads don't speed up CPU-bound Python work (because of the GIL).

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from time import perf_counter

def cpu(n: int) -> int:
    s = 0
    for i in range(n):
        s += i * i
    return s

def run(executor_cls, workers: int, tasks: int, n: int) -> float:
    t0 = perf_counter()
    with executor_cls(max_workers=workers) as ex:
        list(ex.map(cpu, [n] * tasks))
    return perf_counter() - t0

if __name__ == "__main__":
    tasks, n = 8, 25_000_000  # adjust n up/down if it's too slow/fast
    print("1 thread :", run(ThreadPoolExecutor, 1, tasks, n))
    print("8 threads:", run(ThreadPoolExecutor, 8, tasks, n), " <-- usually ~same (GIL)")
    print("8 procs  :", run(ProcessPoolExecutor, 8, tasks, n), " <-- usually faster (multi-core)")