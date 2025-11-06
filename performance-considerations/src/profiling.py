from __future__ import annotations

import cProfile
import pstats
import timeit
import tracemalloc


def work(n: int = 40000) -> int:
    # Some CPU work
    return sum(i * i % 97 for i in range(n))


def profile_work():
    print("-- cProfile + pstats --")
    profiler = cProfile.Profile()
    profiler.enable()
    _ = work(80_000)
    profiler.disable()
    stats = pstats.Stats(profiler).strip_dirs().sort_stats("cumulative")
    stats.print_stats(10)


def timeit_work():
    print("-- timeit --")
    t = timeit.timeit(lambda: work(40_000), number=5)
    print(f"Average {t/5:.6f}s over 5 runs")


def memory_profile():
    print("-- tracemalloc --")
    tracemalloc.start()
    _ = [bytes(1024) for _ in range(20_000)]  # allocate ~20MB
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current: {current/1e6:.1f}MB, Peak: {peak/1e6:.1f}MB")
    tracemalloc.stop()


def main():
    profile_work()
    timeit_work()
    memory_profile()


if __name__ == "__main__":
    main()
