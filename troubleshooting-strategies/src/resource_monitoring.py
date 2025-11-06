from __future__ import annotations

"""Resource Monitoring Demo

Sample CPU, memory, and (simulated) network usage. Uses psutil if available; falls back to /proc.
"""

import time
import shutil

try:
    import psutil  # type: ignore
except ImportError:  # graceful fallback
    psutil = None  # type: ignore


def cpu_memory_snapshot():
    if psutil:
        proc = psutil.Process()
        cpu = psutil.cpu_percent(interval=0.2)
        mem = proc.memory_info().rss / (1024 * 1024)
        return {"cpu_percent": cpu, "rss_mb": round(mem, 2)}
    # Fallback: parse /proc/stat and /proc/self/status (very rough)
    with open("/proc/self/status", "r", encoding="utf-8") as f:
        rss = 0
        for line in f:
            if line.startswith("VmRSS:"):
                parts = line.split()
                rss = int(parts[1]) / 1024  # kB -> MB
                break
    return {"cpu_percent": "n/a", "rss_mb": round(rss, 2)}


def network_snapshot():
    if psutil:
        net = psutil.net_io_counters()
        return {"bytes_sent": net.bytes_sent, "bytes_recv": net.bytes_recv}
    # Fallback: simple read of /proc/net/dev
    with open("/proc/net/dev", "r", encoding="utf-8") as f:
        lines = f.readlines()[2:]
    total_sent = 0
    total_recv = 0
    for line in lines:
        parts = line.split()
        if len(parts) >= 17:
            total_recv += int(parts[1])
            total_sent += int(parts[9])
    return {"bytes_sent": total_sent, "bytes_recv": total_recv}


def demo_sampling(samples: int = 3, delay: float = 0.5):
    print("Sampling resource usage:")
    for i in range(samples):
        snap = cpu_memory_snapshot()
        net = network_snapshot()
        cols = shutil.get_terminal_size().columns
        print(f"{i}: CPU={snap['cpu_percent']}% RSS={snap['rss_mb']}MB sent={net['bytes_sent']} recv={net['bytes_recv']}")
        time.sleep(delay)


def main():
    demo_sampling()


if __name__ == "__main__":
    main()
