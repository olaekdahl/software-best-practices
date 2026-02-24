"""
Demo 03 - Concurrency: asyncio vs threading vs multiprocessing
================================================================
Demonstrates choosing the right concurrency model.

Instructor talking points:
- I/O-bound -> asyncio or threading
- CPU-bound -> multiprocessing (bypass GIL)
- asyncio.TaskGroup for structured concurrency (Python 3.11+)
- Always cap concurrency (semaphores, pool sizes)
- Compare throughput and latency

Run: python main.py
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from math import sqrt


# ============================================================================
# I/O-bound work simulation
# ============================================================================

def io_task_sync(task_id: int, duration: float = 0.1) -> str:
    """Simulate a blocking I/O call (e.g., HTTP request, DB query)."""
    time.sleep(duration)
    return f"io-{task_id}-done"


async def io_task_async(task_id: int, duration: float = 0.1) -> str:
    """Simulate a non-blocking I/O call."""
    await asyncio.sleep(duration)
    return f"io-{task_id}-done"


# ============================================================================
# CPU-bound work simulation
# ============================================================================

def cpu_task(n: int) -> float:
    """CPU-intensive computation (checking primes up to n)."""
    count = 0
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(sqrt(num)) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


# ============================================================================
# Approach 1: Sequential (baseline)
# ============================================================================

def run_sequential_io(num_tasks: int) -> float:
    """Run I/O tasks sequentially."""
    start = time.perf_counter()
    results = []
    for i in range(num_tasks):
        results.append(io_task_sync(i))
    elapsed = time.perf_counter() - start
    return elapsed


def run_sequential_cpu(tasks: list[int]) -> float:
    """Run CPU tasks sequentially."""
    start = time.perf_counter()
    results = [cpu_task(n) for n in tasks]
    elapsed = time.perf_counter() - start
    return elapsed


# ============================================================================
# Approach 2: Threading (good for I/O-bound)
# ============================================================================

def run_threaded_io(num_tasks: int, max_workers: int = 10) -> float:
    """Run I/O tasks with ThreadPoolExecutor."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(io_task_sync, i) for i in range(num_tasks)]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start
    return elapsed


def run_threaded_cpu(tasks: list[int], max_workers: int = 4) -> float:
    """Run CPU tasks with ThreadPoolExecutor (limited by GIL)."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(cpu_task, n) for n in tasks]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - start
    return elapsed


# ============================================================================
# Approach 3: asyncio (best for I/O-bound)
# ============================================================================

async def run_async_io(num_tasks: int) -> float:
    """Run I/O tasks with asyncio (concurrent coroutines)."""
    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(io_task_async(i)) for i in range(num_tasks)]
    results = [t.result() for t in tasks]
    elapsed = time.perf_counter() - start
    return elapsed


async def run_async_io_with_semaphore(num_tasks: int, max_concurrent: int = 10) -> float:
    """Run I/O tasks with asyncio + semaphore (bounded concurrency)."""
    sem = asyncio.Semaphore(max_concurrent)

    async def bounded_task(task_id: int) -> str:
        async with sem:
            return await io_task_async(task_id)

    start = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(bounded_task(i)) for i in range(num_tasks)]
    results = [t.result() for t in tasks]
    elapsed = time.perf_counter() - start
    return elapsed


# ============================================================================
# Approach 4: Multiprocessing (best for CPU-bound)
# ============================================================================

def run_multiprocess_cpu(tasks: list[int], max_workers: int = 4) -> float:
    """Run CPU tasks with ProcessPoolExecutor (bypasses GIL)."""
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(cpu_task, tasks))
    elapsed = time.perf_counter() - start
    return elapsed


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Concurrency Models Comparison ===\n")
    num_io_tasks = 20

    # --- I/O-bound comparison ---
    print(f"--- I/O-Bound ({num_io_tasks} tasks, 100ms each) ---\n")

    t_seq = run_sequential_io(num_io_tasks)
    print(f"  Sequential:           {t_seq:.3f}s")

    t_thread = run_threaded_io(num_io_tasks)
    print(f"  ThreadPool (10):      {t_thread:.3f}s ({t_seq / t_thread:.1f}x speedup)")

    t_async = asyncio.run(run_async_io(num_io_tasks))
    print(f"  asyncio TaskGroup:    {t_async:.3f}s ({t_seq / t_async:.1f}x speedup)")

    t_bounded = asyncio.run(run_async_io_with_semaphore(num_io_tasks, 5))
    print(f"  asyncio + semaphore:  {t_bounded:.3f}s ({t_seq / t_bounded:.1f}x speedup)")
    print()

    # --- CPU-bound comparison ---
    cpu_tasks = [50_000] * 4
    print(f"--- CPU-Bound ({len(cpu_tasks)} tasks, primes up to 50K) ---\n")

    t_seq_cpu = run_sequential_cpu(cpu_tasks)
    print(f"  Sequential:           {t_seq_cpu:.3f}s")

    t_thread_cpu = run_threaded_cpu(cpu_tasks)
    print(f"  ThreadPool:           {t_thread_cpu:.3f}s "
          f"({t_seq_cpu / t_thread_cpu:.1f}x - GIL limited)")

    t_multi_cpu = run_multiprocess_cpu(cpu_tasks)
    print(f"  ProcessPool:          {t_multi_cpu:.3f}s "
          f"({t_seq_cpu / t_multi_cpu:.1f}x speedup)")
    print()

    # --- Decision guide ---
    print("--- Concurrency Decision Guide ---")
    print()
    print("  Work Type    | Best Approach         | Why")
    print("  ------------ | --------------------- | ---")
    print("  I/O-bound    | asyncio + TaskGroup   | Non-blocking, low overhead")
    print("  I/O-bound    | ThreadPoolExecutor    | If using blocking libraries")
    print("  CPU-bound    | ProcessPoolExecutor   | Bypasses GIL")
    print("  Mixed        | asyncio + offload CPU | run_in_executor for CPU work")
    print()
    print("  Always cap concurrency with semaphores or pool sizes.")
    print("  For Python 3.11+, use asyncio.TaskGroup for structured concurrency.")


if __name__ == "__main__":
    main()
