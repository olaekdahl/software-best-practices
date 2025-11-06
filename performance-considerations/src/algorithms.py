from __future__ import annotations

import random
import timeit
import heapq


def benchmark_membership(n: int = 60_000, trials: int = 3):
    data = list(range(n))
    targets = [random.randint(0, n * 2) for _ in range(1_000)]
    setup_list = "data=data; targets=targets"
    setup_set = "s=set(data); targets=targets"
    g = {"data": data, "targets": targets}
    t_list = timeit.timeit(
        stmt="sum(1 for x in targets if x in data)",
        setup="pass",
        number=trials,
        globals=g,
    )
    g_with_set = {"data": data, "targets": targets, "s": set(data)}
    t_set = timeit.timeit(
        stmt="sum(1 for x in targets if x in s)",
        setup="pass",
        number=trials,
        globals=g_with_set,
    )
    print(f"Membership test: list O(n) vs set O(1) avg over {trials} runs")
    print(f"  list: {t_list:.4f}s, set: {t_set:.4f}s")


def two_sum_naive(nums: list[int], target: int) -> tuple[int, int] | None:
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return i, j
    return None


def two_sum_hash(nums: list[int], target: int) -> tuple[int, int] | None:
    seen = {}
    for j, v in enumerate(nums):
        need = target - v
        if need in seen:
            return seen[need], j
        seen[v] = j
    return None


def benchmark_two_sum(n: int = 20_000):
    nums = [random.randint(0, 1000) for _ in range(n)]
    target = nums[-1] + nums[-2]
    t1 = timeit.timeit(lambda: two_sum_naive(nums, target), number=1)
    t2 = timeit.timeit(lambda: two_sum_hash(nums, target), number=5) / 5
    print(f"Two-sum O(n^2) vs O(n) on n={n}")
    print(f"  naive once: {t1:.4f}s, hash avg: {t2:.4f}s")


def benchmark_topk(n: int = 200_000, k: int = 10, trials: int = 3):
    data = [random.random() for _ in range(n)]
    t_sort = timeit.timeit(lambda: sorted(data, reverse=True)[:k], number=trials)
    t_heap = timeit.timeit(lambda: heapq.nlargest(k, data), number=trials)
    print(f"Top-{k}: full sort O(n log n) vs heap nlargest O(n log k), n={n}")
    print(f"  sort: {t_sort:.4f}s, heap: {t_heap:.4f}s (over {trials} runs)")


def main():
    print("-- algorithms & data structures --")
    benchmark_membership()
    benchmark_two_sum()
    benchmark_topk()


if __name__ == "__main__":
    main()
