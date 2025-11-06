# Performance Considerations

Practical, runnable Python demos showing how to write faster code, avoid common performance pitfalls, profile/benchmark, and apply optimization strategies.

## What you'll learn

- Writing performant code: pick efficient algorithms and data structures
- Common performance pitfalls: excessive I/O, memory leaks, unnecessary work, blocking calls
- Profiling and benchmarking: cProfile, pstats, timeit, tracemalloc
- Optimization strategies: caching, lazy loading/streaming, concurrency/parallelism, DB query tuning

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
# Only stdlib used; no extra requirements

# Algorithms and data-structures micro-benchmarks
make -C performance-considerations demo-algorithms

# Pitfalls (I/O, memory, unnecessary computation, blocking)
make -C performance-considerations demo-pitfalls

# Profiling & benchmarking (cProfile, timeit, tracemalloc)
make -C performance-considerations demo-profiling

# Optimization strategies (caching, lazy loading)
make -C performance-considerations demo-optimization

# Concurrency & parallelism (IO-bound: threads; CPU-bound: processes)
make -C performance-considerations demo-concurrency

# Database queries: N+1 vs JOIN
make -C performance-considerations demo-db
```

## Folder layout

- `src/algorithms.py` – micro-benchmarks: set vs list membership, top-k via heap, two-sum O(n^2) vs O(n)
- `src/pitfalls.py` – excessive I/O, memory growth pattern, repeated work, blocking calls
- `src/profiling.py` – cProfile + pstats, timeit, tracemalloc examples
- `src/optimization.py` – caching with lru_cache, lazy file streaming vs eager load
- `src/concurrency_demo.py` – IO-bound with threads, CPU-bound with processes
- `src/db_queries.py` – SQLite N+1 queries vs single JOIN/GROUP BY

Tips:

- Always measure before and after changes, don’t optimize blindly.
- Focus on algorithmic complexity first; micro-optimizations come last.
- Prefer streaming and batching for I/O and data processing.
- For IO-bound tasks, use threading/async; for CPU-bound tasks, consider multiprocessing.