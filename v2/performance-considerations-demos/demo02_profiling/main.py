"""
Demo 02 - Profiling and Benchmarking
=======================================
Demonstrates profiling tools to find hotspots before optimizing.

Instructor talking points:
- Measure before optimizing (never guess)
- timeit for microbenchmarks
- cProfile for function-level profiling
- Compare before/after optimization
- Establish baselines

Run: python main.py
"""

from __future__ import annotations

import cProfile
import io
import pstats
import time
import timeit
from functools import lru_cache


# ============================================================================
# Functions to profile: naive vs optimized
# ============================================================================

def fibonacci_naive(n: int) -> int:
    """Naive recursive fibonacci - exponential time O(2^n)."""
    if n <= 1:
        return n
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


@lru_cache(maxsize=None)
def fibonacci_cached(n: int) -> int:
    """Memoized fibonacci - O(n) time."""
    if n <= 1:
        return n
    return fibonacci_cached(n - 1) + fibonacci_cached(n - 2)


def fibonacci_iterative(n: int) -> int:
    """Iterative fibonacci - O(n) time, O(1) space."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# --- String building ---

def build_string_concat(n: int) -> str:
    """O(n^2) string concatenation."""
    result = ""
    for i in range(n):
        result += f"item-{i} "
    return result


def build_string_join(n: int) -> str:
    """O(n) string building with join."""
    return " ".join(f"item-{i}" for i in range(n))


def build_string_list(n: int) -> str:
    """O(n) string building with list append."""
    parts = []
    for i in range(n):
        parts.append(f"item-{i}")
    return " ".join(parts)


# --- Search ---

def search_linear(data: list[int], target: int) -> int:
    """O(n) linear search."""
    for i, val in enumerate(data):
        if val == target:
            return i
    return -1


def search_set(data: set[int], target: int) -> bool:
    """O(1) set lookup."""
    return target in data


# ============================================================================
# Profiling utilities
# ============================================================================

def profile_function(func, *args, label: str = "") -> None:
    """Profile a function with cProfile and display results."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(10)

    print(f"\n  --- cProfile: {label or func.__name__} ---")
    for line in stream.getvalue().splitlines()[:12]:
        print(f"  {line}")


def benchmark(label: str, stmt: str, setup: str = "", number: int = 1000) -> float:
    """Run a timeit benchmark and display results."""
    result = timeit.timeit(stmt, setup=setup, number=number, globals=globals())
    per_call = result / number * 1000  # ms
    print(f"  {label}: {per_call:.4f} ms/call ({number} iterations)")
    return per_call


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Profiling and Benchmarking ===\n")

    # --- Microbenchmarks with timeit ---
    print("--- timeit Microbenchmarks ---\n")

    print("  Fibonacci(20):")
    benchmark("  Naive (recursive)", "fibonacci_naive(20)", number=100)
    benchmark("  Cached (lru_cache)", "fibonacci_cached(20)", number=10_000)
    benchmark("  Iterative", "fibonacci_iterative(20)", number=10_000)
    print()

    print("  String building (5000 items):")
    benchmark("  Concatenation", "build_string_concat(5000)", number=10)
    benchmark("  Join (generator)", "build_string_join(5000)", number=100)
    benchmark("  List + Join", "build_string_list(5000)", number=100)
    print()

    print("  Search (100K items, worst case):")
    data_list = list(range(100_000))
    data_set = set(data_list)
    target = 99_999

    t1 = timeit.timeit(lambda: search_linear(data_list, target), number=100)
    t2 = timeit.timeit(lambda: search_set(data_set, target), number=100)
    print(f"  Linear search: {t1 / 100 * 1000:.4f} ms/call")
    print(f"  Set lookup:    {t2 / 100 * 1000:.6f} ms/call")
    print(f"  Speedup:       {t1 / t2:.0f}x")
    print()

    # --- cProfile for function-level profiling ---
    print("--- cProfile Function Profiling ---")
    profile_function(fibonacci_naive, 25, label="fibonacci_naive(25)")
    print()

    # --- Optimization comparison ---
    print("--- Before/After Comparison ---\n")

    comparisons = [
        ("Fibonacci(30)", "fibonacci_naive(30)", "fibonacci_iterative(30)", 3, 10_000),
        ("String build (1K)", "build_string_concat(1000)", "build_string_join(1000)", 100, 1000),
    ]

    for label, before_stmt, after_stmt, n_before, n_after in comparisons:
        t_before = timeit.timeit(before_stmt, number=n_before, globals=globals())
        t_after = timeit.timeit(after_stmt, number=n_after, globals=globals())
        ms_before = t_before / n_before * 1000
        ms_after = t_after / n_after * 1000
        speedup = ms_before / ms_after if ms_after > 0 else float("inf")
        print(f"  {label}:")
        print(f"    Before: {ms_before:.4f} ms/call")
        print(f"    After:  {ms_after:.4f} ms/call")
        print(f"    Speedup: {speedup:.1f}x")
        print()

    print("--- Key Takeaways ---")
    print("1. ALWAYS measure before optimizing")
    print("2. timeit for quick microbenchmarks")
    print("3. cProfile for finding hotspot functions")
    print("4. Compare before/after with consistent methodology")
    print("5. Profile with realistic data sizes")
    print("6. py-spy for production profiling (sampling, low overhead)")


if __name__ == "__main__":
    main()
