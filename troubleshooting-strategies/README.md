# Troubleshooting Strategies for Developers

Runnable demos that teach a systematic approach to diagnosing and fixing issues, with practical tooling for logs, traces, debugging, and resource monitoring.

## What you'll learn

- Foundations of Troubleshooting
  - Systematic approach: reproduce → isolate → identify root cause → fix → verify
  - Differentiate symptoms vs root causes
  - Common pitfalls: confirmation bias, skipping steps, over‑fixating on tools
- Tools and Techniques
  - Reading and interpreting logs
  - Using stack traces effectively
  - Built‑in debugging tools (traceback, logging module, VS Code debugger tips)
  - Monitoring resource usage (CPU, memory, network)

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
# Optional: install psutil for richer resource monitoring
# pip install psutil

# Foundations walkthrough
make -C troubleshooting-strategies demo-foundations

# Logs & stack traces
make -C troubleshooting-strategies demo-logs

# Debugging tools (non-interactive demo; see notes for attaching VS Code)
make -C troubleshooting-strategies demo-debugging

# Resource monitoring (falls back to /proc if psutil missing)
make -C troubleshooting-strategies demo-monitor

# Async debugging (inspect running asyncio task stacks)
make -C troubleshooting-strategies demo-async
```

## VS Code Debugger (optional)

- Open `src/debugging_tools.py`, set a breakpoint on the indicated line, and run the Python: Debug file command.
- Or run with a breakpoint hook via env var (will pause execution):
  - `DEMO_DEBUG=1 python troubleshooting-strategies/src/debugging_tools.py`

## Contents

- `src/foundations.py` – step‑by‑step reproduce→isolate→identify→fix→verify with pitfalls explained
- `src/logs_and_traces.py` – logging configuration, stack traces, and how to interpret them
- `src/debugging_tools.py` – logging levels, assertions, optional breakpoint hook (no blocking by default)
- `src/resource_monitoring.py` – CPU/memory/network sampling with psutil when available, otherwise /proc
- `src/resource_monitoring.py` – CPU/memory/network sampling with psutil when available, otherwise /proc
- `src/async_debug.py` – enumerate tasks, inspect their stacks, structured async exception handling

Pro tip: Always measure and make one change at a time; verify the effect before moving on.

## Cheat Sheet: Logs, Traces & Commands

### Log Levels (Python logging)
- DEBUG: Detailed internal state for tracing logic.
- INFO: High-level progress / milestones.
- WARNING: Something unexpected but not fatal.
- ERROR: An operation failed; still running.
- CRITICAL: Process/app is in a bad state; likely exit.

### Common Log Patterns
- Correlation IDs: Add a request or trace ID to each log line for multi-service debugging.
- Structured logs: Use JSON (e.g. `json.dumps({...})`) to make filtering easier.
- Rate limiting: Avoid flooding logs inside tight loops—aggregate counts.
- Redaction: Strip secrets/PII before logging (`password`, tokens, emails). 

### Reading Stack Traces
1. Start at the bottom: locate the originating exception message.
2. Move upward: inspect each frame to see the call chain.
3. Identify the first frame inside your code (not library code) — usually where the fix lives.
4. Reproduce under debugger, inspect local variables in suspect frame.

### Useful Commands & Snippets
```bash
# Show last 50 lines of a log file
tail -n 50 app.log

# Follow logs live
tail -f app.log

# Grep for ERROR lines
grep -i "error" app.log | head

# Count log entries by level (simple heuristic)
grep -E "INFO|ERROR|WARNING" app.log | cut -d' ' -f3 | sort | uniq -c

# Capture Python stack trace for a running process (Linux)
python -c "import faulthandler,signal,os; faulthandler.register(signal.SIGUSR1); print('Send SIGUSR1 to dump stack: ', os.getpid())"
kill -USR1 <pid>
```

### Debugging Checklist
- Reproduce reliably (if not, add instrumentation or widen input cases).
- Confirm symptom vs root cause (don’t patch symptoms only).
- Change one variable at a time; keep a short diary of attempts.
- Add temporary DEBUG logs near suspected branch; remove them once solved.
- After fix: regression test + monitor logs for silent failures.

### Avoid Pitfalls
- Confirmation bias: Actively seek disconfirming evidence.
- Skipping steps: Document reproduction before coding a fix.
- Tool fixation: Use tools to augment thought, not replace hypotheses.

