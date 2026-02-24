#!/usr/bin/env python3
"""
Living Documentation Generator
================================
Extracts documentation from Python source code using introspection
and generates markdown API references, Mermaid state diagrams,
and changelogs from conventional commits.

Usage:
    python generate_docs.py

Output:
    output/api-reference.md   - API reference from docstrings
    output/order-states.mmd   - State diagram from transition annotations
    output/changelog.md       - Changelog from conventional commits
"""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path

# Import the domain module to introspect
from order_domain import Order, OrderItem, OrderRepository, OrderStatus


# ============================================================================
# Documentation extraction
# ============================================================================

@dataclass
class ClassDoc:
    """Extracted documentation for a class."""
    name: str
    docstring: str
    attributes: list[dict]
    methods: list[dict]


def extract_class_doc(cls: type) -> ClassDoc:
    """Extract documentation from a class using introspection."""
    # Get attributes from dataclass fields
    attrs = []
    if hasattr(cls, "__dataclass_fields__"):
        for name, f in cls.__dataclass_fields__.items():
            attr_doc = ""
            if cls.__doc__:
                for line in cls.__doc__.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith(f"{name}:"):
                        attr_doc = stripped.split(":", 1)[1].strip()
            attrs.append({
                "name": name,
                "type": str(f.type) if f.type else "Any",
                "doc": attr_doc,
            })

    # Get methods (skip private except __init__)
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_") and name != "__init__":
            continue
        sig = inspect.signature(method)
        params = [
            {
                "name": p.name,
                "type": (
                    str(p.annotation)
                    if p.annotation != inspect.Parameter.empty
                    else "Any"
                ),
            }
            for p in sig.parameters.values()
            if p.name != "self"
        ]
        methods.append({
            "name": name,
            "signature": str(sig),
            "docstring": inspect.getdoc(method) or "",
            "parameters": params,
            "return_type": (
                str(sig.return_annotation)
                if sig.return_annotation != inspect.Signature.empty
                else "None"
            ),
        })

    # Get properties
    for name, prop in inspect.getmembers(
        cls, predicate=lambda x: isinstance(x, property)
    ):
        ret = "Any"
        if prop.fget and "return" in prop.fget.__annotations__:
            ret = str(prop.fget.__annotations__["return"])
        methods.append({
            "name": name,
            "signature": f"() -> {ret}",
            "docstring": inspect.getdoc(prop) or "",
            "parameters": [],
            "return_type": "property",
        })

    return ClassDoc(
        name=cls.__name__,
        docstring=inspect.getdoc(cls) or "",
        attributes=attrs,
        methods=methods,
    )


def generate_class_markdown(doc: ClassDoc) -> str:
    """Generate markdown documentation for a class."""
    lines = [f"## `{doc.name}`", ""]

    if doc.docstring:
        lines.append(doc.docstring)
        lines.append("")

    if doc.attributes:
        lines.append("### Attributes")
        lines.append("")
        lines.append("| Name | Type | Description |")
        lines.append("|------|------|-------------|")
        for attr in doc.attributes:
            lines.append(
                f"| `{attr['name']}` | `{attr['type']}` | {attr['doc']} |"
            )
        lines.append("")

    if doc.methods:
        lines.append("### Methods")
        lines.append("")
        for method in doc.methods:
            lines.append(f"#### `{method['name']}{method['signature']}`")
            lines.append("")
            if method["docstring"]:
                lines.append(method["docstring"])
            lines.append("")

    return "\n".join(lines)


# ============================================================================
# State diagram generation
# ============================================================================

def generate_state_diagram(cls: type) -> str:
    """Generate a Mermaid state diagram from class docstrings.

    Looks for 'Transitions: X -> Y' patterns in method docstrings.
    """
    transitions = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        doc = inspect.getdoc(method) or ""
        for line in doc.split("\n"):
            if "Transitions:" in line:
                # Parse lines like "Transitions: DRAFT -> SUBMITTED"
                # or "Transitions: DRAFT -> CANCELLED, SUBMITTED -> CANCELLED"
                trans_part = line.split("Transitions:")[1].strip()
                for t in trans_part.split(","):
                    t = t.strip()
                    parts = t.split("->")
                    if len(parts) == 2:
                        src = parts[0].strip()
                        dst = parts[1].strip()
                        if src and dst:
                            transitions.append((src, dst, name))

    lines = [
        "%%{init: {'theme': 'neutral'}}%%",
        "stateDiagram-v2",
        "    [*] --> DRAFT : create()",
    ]
    for src, dst, action in transitions:
        lines.append(f"    {src} --> {dst} : {action}()")
    lines.append("    DELIVERED --> [*]")
    lines.append("    CANCELLED --> [*]")

    return "\n".join(lines)


# ============================================================================
# Changelog generation
# ============================================================================

def generate_changelog(commits: list[dict]) -> str:
    """Generate a changelog from conventional commit messages."""
    categories: dict[str, tuple[str, list]] = {
        "feat": ("Features", []),
        "fix": ("Bug Fixes", []),
        "perf": ("Performance", []),
        "docs": ("Documentation", []),
        "refactor": ("Refactoring", []),
        "test": ("Tests", []),
    }

    for commit in commits:
        msg = commit["message"]
        for prefix, (_, items) in categories.items():
            if msg.startswith(f"{prefix}:") or msg.startswith(f"{prefix}("):
                desc = msg.split(":", 1)[1].strip() if ":" in msg else msg
                items.append({
                    "description": desc,
                    "hash": commit["hash"],
                    "author": commit.get("author", "unknown"),
                })
                break

    lines = ["# Changelog", "", "## v2.2.0 (2026-02-15)", ""]
    for _, (title, items) in categories.items():
        if items:
            lines.append(f"### {title}")
            lines.append("")
            for item in items:
                lines.append(f"- {item['description']} ({item['hash'][:7]})")
            lines.append("")

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("Living Documentation Generator")
    print("=" * 40)

    # --- Generate API reference ---
    print("\n1. Generating API reference from docstrings...")
    classes_to_document = [OrderItem, Order, OrderRepository]
    all_docs = []

    for cls in classes_to_document:
        doc = extract_class_doc(cls)
        md = generate_class_markdown(doc)
        all_docs.append(md)
        print(
            f"   {cls.__name__}: "
            f"{len(doc.attributes)} attributes, "
            f"{len(doc.methods)} methods"
        )

    full_doc = "# Order Service API Reference\n\n"
    full_doc += "*Auto-generated from source code. Do not edit manually.*\n\n"
    full_doc += "---\n\n".join(all_docs)

    (output_dir / "api-reference.md").write_text(full_doc)
    print(f"   Written to: output/api-reference.md ({len(full_doc)} chars)")

    # --- Generate state diagram ---
    print("\n2. Generating state diagram from transition annotations...")
    diagram = generate_state_diagram(Order)
    (output_dir / "order-states.mmd").write_text(diagram)
    transition_count = diagram.count("-->") - 1  # subtract the [*] line
    print(f"   Found {transition_count} transitions")
    print(f"   Written to: output/order-states.mmd")

    # --- Generate changelog ---
    print("\n3. Generating changelog from conventional commits...")
    sample_commits = [
        {"hash": "abc1234567", "message": "feat: add order cancellation within 1 hour", "author": "alice"},
        {"hash": "def2345678", "message": "fix: prevent negative quantities in order items", "author": "bob"},
        {"hash": "ghi3456789", "message": "perf: add index on orders.customer_id", "author": "charlie"},
        {"hash": "jkl4567890", "message": "docs: update API reference for v2.2", "author": "alice"},
        {"hash": "mno5678901", "message": "feat(auth): add JWT refresh token endpoint", "author": "diana"},
        {"hash": "pqr6789012", "message": "fix: handle race condition in inventory check", "author": "bob"},
        {"hash": "stu7890123", "message": "test: add property-based tests for Order total", "author": "charlie"},
        {"hash": "vwx8901234", "message": "refactor: extract PaymentAdapter from OrderService", "author": "alice"},
    ]
    changelog = generate_changelog(sample_commits)
    (output_dir / "changelog.md").write_text(changelog)
    print(f"   Written to: output/changelog.md")

    print("\nDone. All documentation generated in output/")


if __name__ == "__main__":
    main()
