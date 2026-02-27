from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMOS = ROOT / "demos"

def main() -> None:
    apps = sorted(DEMOS.glob("*/app.py"))
    for app in apps:
        rel = app.relative_to(ROOT)
        print("\n" + "=" * 80)
        print(f"Running: {rel}")
        print("=" * 80)
        runpy.run_path(str(app), run_name="__main__")

if __name__ == "__main__":
    main()
