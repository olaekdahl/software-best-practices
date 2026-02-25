"""
Demo 05 - Secure Pipeline: SAST, SCA, Secret Scanning
========================================================
Simulates a security-focused CI pipeline with automated scanning.

Instructor talking points:
- Bandit for Python SAST (static analysis security testing)
- pip-audit for SCA (software composition analysis)
- detect-secrets for secret scanning
- Security gates in CI/CD
- SBOM generation

Run: python main.py
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ============================================================================
# Severity levels
# ============================================================================

class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    """A security finding from a scanner."""
    scanner: str
    severity: Severity
    title: str
    description: str
    file: str = ""
    line: int = 0


# ============================================================================
# Scanner 1: Secret Scanner
# ============================================================================

# Patterns that indicate hardcoded secrets
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
     "Hardcoded API key"),
    (r"(?i)(secret|password|passwd|pwd)\s*=\s*['\"][^'\"]{8,}['\"]",
     "Hardcoded password/secret"),
    (r"(?i)(token)\s*=\s*['\"][a-zA-Z0-9_\-\.]{20,}['\"]",
     "Hardcoded token"),
    (r"(?:sk|pk)[-_](?:live|test|prod)[-_][a-zA-Z0-9]{10,}",
     "API key pattern (Stripe-like)"),
    (r"-----BEGIN (?:RSA|EC|DSA|OPENSSH) PRIVATE KEY-----",
     "Private key in source"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*=\s*['\"][A-Za-z0-9/+=]{20,}",
     "AWS secret access key"),
]


def scan_for_secrets(code: str, filename: str = "") -> list[Finding]:
    """Scan code for hardcoded secrets."""
    findings = []
    for pattern, description in SECRET_PATTERNS:
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count("\n") + 1
            findings.append(Finding(
                scanner="secret-scanner",
                severity=Severity.HIGH,
                title=description,
                description=f"Potential secret found: {match.group()[:30]}...",
                file=filename,
                line=line_num,
            ))
    return findings


# ============================================================================
# Scanner 2: Simple SAST (Python security patterns)
# ============================================================================

SAST_PATTERNS = [
    (r"eval\s*\(", "Use of eval()", Severity.HIGH,
     "eval() can execute arbitrary code. Use ast.literal_eval() for data."),
    (r"exec\s*\(", "Use of exec()", Severity.HIGH,
     "exec() can execute arbitrary code. Avoid or sandbox strictly."),
    (r"pickle\.loads?\s*\(", "Unsafe deserialization", Severity.HIGH,
     "pickle can execute arbitrary code during deserialization."),
    (r"yaml\.load\s*\((?!.*Loader)", "Unsafe YAML load", Severity.MEDIUM,
     "Use yaml.safe_load() instead of yaml.load()."),
    (r"subprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True",
     "Shell injection risk", Severity.HIGH,
     "shell=True with user input enables command injection."),
    (r"os\.system\s*\(", "Use of os.system()", Severity.MEDIUM,
     "os.system() is vulnerable to injection. Use subprocess with shell=False."),
    (r"SELECT.*FROM.*\+|f['\"].*SELECT.*FROM",
     "SQL injection risk", Severity.CRITICAL,
     "String concatenation in SQL queries. Use parameterized queries."),
    (r"assert\s+\w+", "Assert used for validation", Severity.LOW,
     "Asserts are removed with -O flag. Use proper validation."),
    (r"chmod\s*\(\s*0o?777", "World-writable permissions", Severity.MEDIUM,
     "Setting 777 permissions is overly permissive."),
]


def scan_sast(code: str, filename: str = "") -> list[Finding]:
    """Run simple SAST patterns against code."""
    findings = []
    for pattern, title, severity, description in SAST_PATTERNS:
        for match in re.finditer(pattern, code, re.IGNORECASE):
            line_num = code[:match.start()].count("\n") + 1
            findings.append(Finding(
                scanner="sast",
                severity=severity,
                title=title,
                description=description,
                file=filename,
                line=line_num,
            ))
    return findings


# ============================================================================
# Scanner 3: Dependency checker (simulated)
# ============================================================================

# Simulated vulnerability database
VULN_DB = {
    "requests": {"affected": "<2.31.0", "cve": "CVE-2023-32681", "severity": Severity.MEDIUM,
                 "description": "Leaking Proxy-Authorization headers"},
    "flask": {"affected": "<3.0.0", "cve": "CVE-2023-30861", "severity": Severity.HIGH,
              "description": "Session cookie vulnerability"},
    "cryptography": {"affected": "<41.0.0", "cve": "CVE-2023-38325", "severity": Severity.HIGH,
                     "description": "SSH certificate parsing vulnerability"},
    "pillow": {"affected": "<10.0.1", "cve": "CVE-2023-44271", "severity": Severity.MEDIUM,
               "description": "Denial of service via crafted image"},
    "urllib3": {"affected": "<2.0.7", "cve": "CVE-2023-45803", "severity": Severity.MEDIUM,
                "description": "Cookie leaking on redirect"},
}


def scan_dependencies(requirements: str) -> list[Finding]:
    """Check dependencies against vulnerability database."""
    findings = []
    for line in requirements.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Parse package name (simplified)
        pkg_name = re.split(r"[>=<!\[]", line)[0].strip().lower()
        if pkg_name in VULN_DB:
            vuln = VULN_DB[pkg_name]
            findings.append(Finding(
                scanner="sca",
                severity=vuln["severity"],
                title=f"{pkg_name}: {vuln['cve']}",
                description=f"{vuln['description']} (affected: {vuln['affected']})",
                file="requirements.txt",
            ))
    return findings


# ============================================================================
# Pipeline runner
# ============================================================================

def run_security_pipeline(
    code_samples: dict[str, str],
    requirements: str,
    fail_on: Severity = Severity.HIGH,
) -> bool:
    """Run all security scanners and report findings.

    Returns True if pipeline passes, False if it should fail.
    """
    all_findings: list[Finding] = []

    print("=" * 60)
    print("SECURITY PIPELINE")
    print("=" * 60)

    # --- Secret scanning ---
    print("\n[1/3] Secret Scanning...")
    for filename, code in code_samples.items():
        findings = scan_for_secrets(code, filename)
        all_findings.extend(findings)
    print(f"  Found {sum(1 for f in all_findings if f.scanner == 'secret-scanner')} issues")

    # --- SAST ---
    print("\n[2/3] Static Analysis (SAST)...")
    for filename, code in code_samples.items():
        findings = scan_sast(code, filename)
        all_findings.extend(findings)
    sast_count = sum(1 for f in all_findings if f.scanner == "sast")
    print(f"  Found {sast_count} issues")

    # --- SCA ---
    print("\n[3/3] Dependency Check (SCA)...")
    dep_findings = scan_dependencies(requirements)
    all_findings.extend(dep_findings)
    print(f"  Found {len(dep_findings)} vulnerable dependencies")

    # --- Report ---
    print("\n" + "=" * 60)
    print("FINDINGS REPORT")
    print("=" * 60)

    by_severity = {}
    for f in all_findings:
        by_severity.setdefault(f.severity, []).append(f)

    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        findings = by_severity.get(severity, [])
        if findings:
            print(f"\n  [{severity.value}] ({len(findings)} findings)")
            for f in findings:
                location = f"{f.file}:{f.line}" if f.line else f.file
                print(f"    - [{f.scanner}] {f.title}")
                print(f"      {f.description}")
                if location:
                    print(f"      Location: {location}")

    # --- Gate decision ---
    fail_level = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}
    gate_level = fail_level[fail_on]
    blocking = [f for f in all_findings if fail_level[f.severity] >= gate_level]

    print("\n" + "=" * 60)
    if blocking:
        print(f"PIPELINE FAILED: {len(blocking)} blocking findings "
              f"(threshold: {fail_on.value})")
        print("=" * 60)
        return False
    else:
        print(f"PIPELINE PASSED: No findings at or above {fail_on.value}")
        print("=" * 60)
        return True


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Secure Pipeline ===\n")

    # --- Sample vulnerable code ---
    vulnerable_code = {
        "app.py": '''
import os
import pickle

API_KEY = "sk-live-a1b2c3d4e5f6g7h8i9j0"
DB_PASSWORD = "super-secret-password-123"

def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)

def process_data(data):
    return eval(data)

def load_config(path):
    with open(path, "rb") as f:
        return pickle.load(f)

def run_command(cmd):
    os.system(cmd)
''',
        "utils.py": '''
import yaml
import subprocess

def parse_config(text):
    return yaml.load(text)

def deploy(branch):
    subprocess.run(f"git push origin {branch}", shell=True)
''',
    }

    requirements = """
requests==2.28.0
flask==2.3.0
cryptography==40.0.0
pillow==9.5.0
urllib3==1.26.0
fastapi==0.109.0
pydantic==2.5.0
"""

    # Run pipeline
    passed = run_security_pipeline(
        vulnerable_code, requirements, fail_on=Severity.HIGH
    )

    print(f"\nPipeline result: {'PASS' if passed else 'FAIL'}")

    print("\n--- CI Integration Commands ---")
    print("  bandit -r src -ll                    # SAST for Python")
    print("  pip-audit -r requirements.txt        # Dependency vulnerabilities")
    print("  detect-secrets scan --all-files       # Secret scanning")
    print("  trivy image myapp:latest              # Container scanning")
    print("  syft myapp:latest -o spdx-json        # SBOM generation")


if __name__ == "__main__":
    main()
