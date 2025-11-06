from __future__ import annotations

"""Async Debugging Demo

Shows how to inspect asyncio task tracebacks/stacks while the event loop is running.

Techniques:
- Enumerate tasks (asyncio.all_tasks)
- Capture stack frames (task.get_stack)
- Use loop.set_exception_handler for structured async errors
- Optionally dump all task stacks on signal (SIGUSR1, Unix)
"""

import asyncio
import signal
import sys
import traceback
from types import FrameType


def task_dump() -> None:
    print("\n[async-debug] Dumping task stacks...")
    for t in asyncio.all_tasks():
        print(f"- Task: {t.get_name()} (done={t.done()})")
        for frame in t.get_stack(limit=5):
            stack = traceback.format_stack(frame)
            # Print the last frame (most relevant)
            print("  frame:")
            print("".join(stack[-1:]).rstrip())


def install_signal_dump(loop: asyncio.AbstractEventLoop) -> None:
    if hasattr(signal, "SIGUSR1"):
        def handler():
            # Schedule dump inside loop thread-safely
            loop.call_soon_threadsafe(task_dump)
        try:
            loop.add_signal_handler(signal.SIGUSR1, handler)
            print(f"[async-debug] Send SIGUSR1 to pid {os.getpid()} to dump task stacks")
        except Exception:
            pass


def exception_handler(loop, context):
    print("\n[async-debug] Exception in task:")
    msg = context.get("message")
    if msg:
        print(" message:", msg)
    exc = context.get("exception")
    if exc:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
    else:
        print(" context:", context)


async def worker(name: str, delay: float):
    await asyncio.sleep(delay)
    if name == "bad":
        raise RuntimeError("simulated async error")
    await asyncio.sleep(0.5)
    return f"ok:{name}"


async def inspector():
    # Periodically dump stacks while tasks run
    for _ in range(3):
        await asyncio.sleep(0.2)
        task_dump()


async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(exception_handler)
    # install_signal_dump(loop)  # optional on Unix

    tasks = [
        asyncio.create_task(worker("good", 0.6), name="worker-good"),
        asyncio.create_task(worker("bad", 0.3), name="worker-bad"),
        asyncio.create_task(inspector(), name="inspector"),
    ]

    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    for t in done:
        if not t.cancelled():
            try:
                _ = t.result()
            except Exception:
                # Already printed by exception handler; suppress
                pass


if __name__ == "__main__":
    asyncio.run(main())
