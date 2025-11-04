#!/usr/bin/env python3
"""
Tiny runner to execute all demo scripts sequentially.
Usage:
  python software-principles-and-patterns/run_all.py [filter]
If [filter] is provided, only paths containing the substring will run.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    ("Overview: messy_code_bad", ROOT/"00-overview"/"messy_code_bad.py"),
    ("Overview: messy_code_refactor", ROOT/"00-overview"/"messy_code_refactor.py"),
    ("Principles: SRP/OCP bad", ROOT/"01-principles"/"srp_ocp_order_processor_bad.py"),
    ("Principles: SRP/OCP good", ROOT/"01-principles"/"srp_ocp_order_processor_good.py"),
    ("Principles: LSP/ISP bad", ROOT/"01-principles"/"lsp_isp_bad.py"),
    ("Principles: LSP/ISP good", ROOT/"01-principles"/"lsp_isp_good.py"),
    ("Principles: DIP logger", ROOT/"01-principles"/"dip_logger_demo.py"),
    ("Principles: DRY/KISS/YAGNI bad", ROOT/"01-principles"/"dry_kiss_yagni_bad.py"),
    ("Principles: DRY/KISS/YAGNI good", ROOT/"01-principles"/"dry_kiss_yagni_good.py"),
    ("Patterns: Factory Method / Singleton", ROOT/"02-patterns"/"factory_method_singleton.py"),
    ("Patterns: Adapter / Facade", ROOT/"02-patterns"/"adapter_facade.py"),
    ("Patterns: Observer / Strategy", ROOT/"02-patterns"/"observer_strategy.py"),
    ("Interactive: smell_spotting", ROOT/"smell_spotting.py"),
]

def main() -> int:
    flt = sys.argv[1] if len(sys.argv) > 1 else None
    for label, path in SCRIPTS:
        if flt and flt.lower() not in str(path).lower() and flt.lower() not in label.lower():
            continue
        print("\n" + "="*80)
        print(f"RUNNING: {label}\nFILE: {path}")
        print("="*80)
        try:
            subprocess.run([sys.executable, str(path)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Script failed: {path} (exit {e.returncode})")
            return e.returncode
    print("\nAll demos finished.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
