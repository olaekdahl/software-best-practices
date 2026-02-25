#!/usr/bin/env python3
"""
Custom Documentation Linter
============================
A simple doc linter that checks markdown files for common issues.

This demonstrates the concept of docs-as-code validation. In practice,
you would use tools like markdownlint, cspell, and lychee, but
understanding how they work helps you write better custom rules.

Usage:
    python lint_docs.py docs/
    python lint_docs.py docs/api-guide.md
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LintIssue:
    """A documentation quality issue."""
    file: str
    line: int
    rule: str
    severity: str  # ERROR, WARNING, INFO
    message: str

    def __str__(self) -> str:
        return f"  [{self.severity}] {self.file}:{self.line} ({self.rule}) {self.message}"


def lint_markdown(filepath: Path) -> list[LintIssue]:
    """Run lint rules against a markdown file."""
    content = filepath.read_text()
    lines = content.split("\n")
    issues: list[LintIssue] = []
    name = str(filepath)

    for i, line in enumerate(lines, 1):
        # Rule: No trailing whitespace
        if line.rstrip() != line and line.strip():
            issues.append(LintIssue(
                name, i, "MD009", "WARNING",
                "Trailing whitespace",
            ))

        # Rule: Headings need a space after #
        if re.match(r"^#+[^ #]", line):
            issues.append(LintIssue(
                name, i, "MD018", "ERROR",
                "No space after heading hash",
            ))

        # Rule: No bare URLs (should be links)
        if re.search(r"(?<!\(|<)https?://\S+(?!\)|>)", line):
            if not line.strip().startswith("[") and not line.strip().startswith("- "):
                issues.append(LintIssue(
                    name, i, "MD034", "WARNING",
                    "Bare URL - wrap in angle brackets or link syntax",
                ))

        # Rule: No TODO/FIXME/TBD in published docs
        if re.search(r"\b(TODO|FIXME|TBD|PLACEHOLDER)\b", line, re.IGNORECASE):
            issues.append(LintIssue(
                name, i, "DOC001", "ERROR",
                "Unresolved TODO/TBD in documentation",
            ))

        # Rule: Line too long (skip code blocks)
        if len(line) > 120 and not line.startswith("```") and not line.startswith("    "):
            issues.append(LintIssue(
                name, i, "MD013", "INFO",
                f"Line length {len(line)} exceeds 120 characters",
            ))

    # Rule: File should end with a newline
    if content and not content.endswith("\n"):
        issues.append(LintIssue(
            name, len(lines), "MD047", "WARNING",
            "File should end with a single newline",
        ))

    # Rule: First line should be a heading
    first_content = next((line for line in lines if line.strip()), "")
    if not first_content.startswith("#"):
        issues.append(LintIssue(
            name, 1, "MD041", "WARNING",
            "First line should be a top-level heading",
        ))

    # Spell check for common misspellings
    common_errors = {
        "teh": "the", "adn": "and", "recieve": "receive",
        "seperate": "separate", "occured": "occurred",
        "enviroment": "environment", "dependancy": "dependency",
        "refrence": "reference", "configuraiton": "configuration",
    }
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```") or line.startswith("    "):
            continue
        for wrong, right in common_errors.items():
            if re.search(rf"\b{wrong}\b", line, re.IGNORECASE):
                issues.append(LintIssue(
                    name, i, "SPELL", "ERROR",
                    f"Misspelling: '{wrong}' -> '{right}'",
                ))

    return issues


def main() -> int:
    """Lint markdown files and report issues."""
    if len(sys.argv) < 2:
        print("Usage: python lint_docs.py <path>")
        print("  path can be a file or directory")
        return 1

    target = Path(sys.argv[1])

    if target.is_file():
        files = [target]
    elif target.is_dir():
        files = sorted(target.rglob("*.md"))
    else:
        print(f"Error: {target} not found")
        return 1

    total_issues = 0
    total_errors = 0

    print(f"\nLinting {len(files)} file(s)...\n")

    for filepath in files:
        issues = lint_markdown(filepath)
        total_issues += len(issues)
        errors = sum(1 for i in issues if i.severity == "ERROR")
        total_errors += errors

        if issues:
            print(f"{filepath} ({len(issues)} issue(s), {errors} error(s)):")
            for issue in issues:
                print(str(issue))
            print()
        else:
            print(f"{filepath}: OK")

    print(f"\nSummary: {total_issues} issue(s), {total_errors} error(s) in {len(files)} file(s)")

    if total_errors > 0:
        print("FAILED: Fix errors before merging.")
        return 1

    print("PASSED: All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
