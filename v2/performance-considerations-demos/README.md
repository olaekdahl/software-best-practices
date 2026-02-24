# Performance Considerations - Demos

Progressive demos from naive performance to resilience patterns.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_naive_performance | Unoptimized code with obvious bottlenecks | Naive |
| demo02_profiling | Profiling with timeit, cProfile, line_profiler | Intermediate |
| demo03_concurrency | asyncio, threading, multiprocessing comparison | Intermediate |
| demo04_caching | Caching strategies with TTL and invalidation | Advanced |
| demo05_resilience | Circuit breaker, retry, timeout, bulkhead | Real-world |

## Setup

```bash
pip install aiohttp
```

## Running

```bash
cd demo01_naive_performance
python main.py
```
