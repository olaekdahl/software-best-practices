"""
Demo 05 - Orchestrated Pipeline with Lineage
===============================================
Full pipeline with task orchestration, dependency management, and data lineage.

Instructor talking points:
- DAG-based orchestration (like Airflow/Prefect)
- Tasks declare dependencies explicitly
- Data lineage: trace any output back to its source
- Idempotent tasks with checkpointing
- Alerting on task failure with retry support

Run: python main.py
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


# ============================================================================
# Task and DAG definitions
# ============================================================================

class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    UPSTREAM_FAILED = "UPSTREAM_FAILED"


@dataclass
class TaskResult:
    """Result of a task execution."""
    status: TaskStatus
    output: Any = None
    error: str = ""
    duration_ms: int = 0
    records_processed: int = 0


@dataclass
class Task:
    """A single task in a pipeline DAG."""
    id: str
    name: str
    func: Callable
    dependencies: list[str] = field(default_factory=list)
    retries: int = 2
    retry_delay: float = 0.1
    result: TaskResult | None = None
    _attempts: int = 0

    def execute(self, context: dict) -> TaskResult:
        """Execute the task with retry logic."""
        for attempt in range(1, self.retries + 1):
            self._attempts = attempt
            start = time.perf_counter()
            try:
                output = self.func(context)
                elapsed = int((time.perf_counter() - start) * 1000)
                self.result = TaskResult(
                    status=TaskStatus.SUCCESS,
                    output=output,
                    duration_ms=elapsed,
                    records_processed=output.get("records", 0) if isinstance(output, dict) else 0,
                )
                return self.result
            except Exception as e:
                elapsed = int((time.perf_counter() - start) * 1000)
                if attempt < self.retries:
                    print(f"      Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay)
                else:
                    self.result = TaskResult(
                        status=TaskStatus.FAILED,
                        error=str(e),
                        duration_ms=elapsed,
                    )
                    return self.result

        # Should not reach here, but just in case
        self.result = TaskResult(status=TaskStatus.FAILED, error="Unknown error")
        return self.result


class DAG:
    """Directed Acyclic Graph for task orchestration."""

    def __init__(self, name: str, schedule: str = "daily"):
        self.name = name
        self.schedule = schedule
        self.tasks: dict[str, Task] = {}
        self._execution_order: list[str] = []

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    def _topological_sort(self) -> list[str]:
        """Sort tasks by dependencies (topological order)."""
        visited: set[str] = set()
        order: list[str] = []

        def visit(task_id: str) -> None:
            if task_id in visited:
                return
            visited.add(task_id)
            task = self.tasks[task_id]
            for dep in task.dependencies:
                if dep in self.tasks:
                    visit(dep)
            order.append(task_id)

        for task_id in self.tasks:
            visit(task_id)

        return order

    def execute(self) -> dict:
        """Execute all tasks in dependency order."""
        self._execution_order = self._topological_sort()
        context: dict[str, Any] = {"dag_name": self.name, "outputs": {}}
        results: dict[str, TaskResult] = {}

        print(f"  Execution order: {' -> '.join(self._execution_order)}")
        print()

        for task_id in self._execution_order:
            task = self.tasks[task_id]

            # Check upstream status
            upstream_failed = any(
                results.get(dep, TaskResult(TaskStatus.PENDING)).status == TaskStatus.FAILED
                for dep in task.dependencies
            )

            if upstream_failed:
                print(f"    [{task_id}] SKIPPED (upstream failed)")
                task.result = TaskResult(status=TaskStatus.UPSTREAM_FAILED)
                results[task_id] = task.result
                continue

            print(f"    [{task_id}] {task.name}...")
            result = task.execute(context)
            results[task_id] = result

            if result.status == TaskStatus.SUCCESS:
                context["outputs"][task_id] = result.output
                print(f"    [{task_id}] SUCCESS ({result.duration_ms}ms, "
                      f"{result.records_processed} records)")
            else:
                print(f"    [{task_id}] FAILED: {result.error}")

        return results


# ============================================================================
# Data lineage tracking
# ============================================================================

@dataclass
class LineageNode:
    """A node in the data lineage graph."""
    id: str
    name: str
    node_type: str  # "source", "transform", "sink"
    metadata: dict = field(default_factory=dict)


@dataclass
class LineageEdge:
    """An edge connecting two lineage nodes."""
    source_id: str
    target_id: str
    transformation: str


class LineageTracker:
    """Tracks data lineage across pipeline stages."""

    def __init__(self):
        self.nodes: dict[str, LineageNode] = {}
        self.edges: list[LineageEdge] = []

    def add_node(self, node: LineageNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str, transformation: str) -> None:
        self.edges.append(LineageEdge(source_id, target_id, transformation))

    def get_upstream(self, node_id: str) -> list[str]:
        """Get all upstream nodes (data sources)."""
        upstream = []
        for edge in self.edges:
            if edge.target_id == node_id:
                upstream.append(edge.source_id)
                upstream.extend(self.get_upstream(edge.source_id))
        return upstream

    def get_downstream(self, node_id: str) -> list[str]:
        """Get all downstream nodes (consumers)."""
        downstream = []
        for edge in self.edges:
            if edge.source_id == node_id:
                downstream.append(edge.target_id)
                downstream.extend(self.get_downstream(edge.target_id))
        return downstream

    def to_mermaid(self) -> str:
        """Generate a Mermaid diagram of the lineage graph."""
        lines = ["%%{init: {'theme': 'neutral'}}%%", "graph LR"]

        # Style nodes by type
        for nid, node in self.nodes.items():
            if node.node_type == "source":
                lines.append(f"    {nid}[({node.name})]")
            elif node.node_type == "sink":
                lines.append(f"    {nid}[[\"{node.name}\"]]")
            else:
                lines.append(f"    {nid}[{node.name}]")

        for edge in self.edges:
            lines.append(f"    {edge.source_id} -->|{edge.transformation}| {edge.target_id}")

        return "\n".join(lines)


# ============================================================================
# Pipeline task implementations
# ============================================================================

def task_extract_sales(context: dict) -> dict:
    """Extract sales data from source."""
    time.sleep(0.02)
    data = [
        {"date": "2025-01-01", "product": "Widget A", "qty": 5, "price": 29.99, "region": "North"},
        {"date": "2025-01-01", "product": "Widget B", "qty": 3, "price": 49.99, "region": "South"},
        {"date": "2025-01-02", "product": "Gadget X", "qty": 1, "price": 199.99, "region": "East"},
        {"date": "2025-01-02", "product": "Widget A", "qty": 7, "price": 29.99, "region": "West"},
        {"date": "2025-01-03", "product": "Widget B", "qty": 10, "price": 49.99, "region": "North"},
    ]
    return {"records": len(data), "data": data}


def task_extract_customers(context: dict) -> dict:
    """Extract customer data."""
    time.sleep(0.01)
    data = [
        {"id": "C100", "name": "Alice Corp", "tier": "gold", "region": "North"},
        {"id": "C101", "name": "Bob Inc", "tier": "silver", "region": "South"},
        {"id": "C102", "name": "Charlie LLC", "tier": "bronze", "region": "East"},
    ]
    return {"records": len(data), "data": data}


def task_validate(context: dict) -> dict:
    """Validate extracted data against contracts."""
    time.sleep(0.01)
    sales = context["outputs"].get("extract_sales", {}).get("data", [])
    errors = []
    valid = []

    for row in sales:
        if row["qty"] <= 0:
            errors.append({"row": row, "error": "invalid quantity"})
        elif row["price"] <= 0:
            errors.append({"row": row, "error": "invalid price"})
        else:
            valid.append(row)

    return {"records": len(valid), "valid": valid, "rejected": len(errors)}


def task_transform(context: dict) -> dict:
    """Transform and enrich data."""
    time.sleep(0.02)
    valid_data = context["outputs"].get("validate", {}).get("valid", [])

    enriched = []
    for row in valid_data:
        enriched.append({
            **row,
            "total": round(row["qty"] * row["price"], 2),
            "processed_at": datetime.now().isoformat(),
        })

    # Aggregate by region
    by_region: dict[str, float] = {}
    for row in enriched:
        by_region[row["region"]] = by_region.get(row["region"], 0) + row["total"]

    return {
        "records": len(enriched),
        "data": enriched,
        "aggregates": {"by_region": by_region},
    }


def task_load(context: dict) -> dict:
    """Load transformed data to destination."""
    time.sleep(0.01)
    transformed = context["outputs"].get("transform", {})
    records = transformed.get("records", 0)
    return {"records": records, "destination": "analytics_db", "status": "loaded"}


def task_generate_report(context: dict) -> dict:
    """Generate analytics report from loaded data."""
    time.sleep(0.01)
    aggregates = context["outputs"].get("transform", {}).get("aggregates", {})
    return {
        "records": 1,
        "report": {
            "title": "Daily Sales Report",
            "generated_at": datetime.now().isoformat(),
            "metrics": aggregates,
        },
    }


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Demo: Orchestrated Pipeline with Lineage ===\n")

    # --- Build the DAG ---
    print("--- Building Pipeline DAG ---\n")
    dag = DAG("daily_sales_pipeline", schedule="0 6 * * *")

    dag.add_task(Task("extract_sales", "Extract Sales Data", task_extract_sales))
    dag.add_task(Task("extract_customers", "Extract Customer Data", task_extract_customers))
    dag.add_task(Task("validate", "Validate Data", task_validate,
                       dependencies=["extract_sales"]))
    dag.add_task(Task("transform", "Transform & Enrich", task_transform,
                       dependencies=["validate", "extract_customers"]))
    dag.add_task(Task("load", "Load to Analytics DB", task_load,
                       dependencies=["transform"]))
    dag.add_task(Task("report", "Generate Report", task_generate_report,
                       dependencies=["transform"]))

    print(f"  Pipeline: {dag.name}")
    print(f"  Schedule: {dag.schedule}")
    print(f"  Tasks: {len(dag.tasks)}")
    print()

    # --- Execute ---
    print("--- Executing Pipeline ---\n")
    results = dag.execute()
    print()

    # --- Show results ---
    print("--- Pipeline Results ---\n")
    total_time = 0
    for task_id, result in results.items():
        status = result.status.value
        total_time += result.duration_ms
        print(f"  {task_id:<20} {status:<15} {result.duration_ms:>5}ms  "
              f"{result.records_processed:>3} records")
    print(f"  {'TOTAL':<20} {'':15} {total_time:>5}ms")
    print()

    # Show aggregates from transform
    transform_output = dag.tasks["transform"].result
    if transform_output and transform_output.output:
        aggs = transform_output.output.get("aggregates", {})
        if "by_region" in aggs:
            print("  Sales by Region:")
            for region, total in sorted(aggs["by_region"].items()):
                print(f"    {region}: ${total:.2f}")
    print()

    # --- Data Lineage ---
    print("--- Data Lineage ---\n")
    lineage = LineageTracker()

    lineage.add_node(LineageNode("pos_db", "POS Database", "source"))
    lineage.add_node(LineageNode("crm_db", "CRM Database", "source"))
    lineage.add_node(LineageNode("extract_sales", "Extract Sales", "transform"))
    lineage.add_node(LineageNode("extract_customers", "Extract Customers", "transform"))
    lineage.add_node(LineageNode("validate", "Validate", "transform"))
    lineage.add_node(LineageNode("transform", "Transform & Enrich", "transform"))
    lineage.add_node(LineageNode("analytics_db", "Analytics DB", "sink"))
    lineage.add_node(LineageNode("report", "Daily Report", "sink"))

    lineage.add_edge("pos_db", "extract_sales", "full extract")
    lineage.add_edge("crm_db", "extract_customers", "incremental")
    lineage.add_edge("extract_sales", "validate", "schema check")
    lineage.add_edge("validate", "transform", "clean + enrich")
    lineage.add_edge("extract_customers", "transform", "join")
    lineage.add_edge("transform", "analytics_db", "upsert")
    lineage.add_edge("transform", "report", "aggregate")

    # Upstream analysis
    print("  Q: Where does the 'Daily Report' data come from?")
    upstream = lineage.get_upstream("report")
    print(f"  A: {' <- '.join(upstream)}")
    print()

    # Downstream analysis
    print("  Q: What is affected if 'POS Database' changes?")
    downstream = lineage.get_downstream("pos_db")
    print(f"  A: {' -> '.join(downstream)}")
    print()

    # Mermaid diagram
    mermaid = lineage.to_mermaid()
    print("  Lineage Diagram (Mermaid):")
    for line in mermaid.split("\n"):
        print(f"    {line}")

    print("\n--- Orchestrated Pipeline Best Practices ---")
    print("1. Define tasks as a DAG with explicit dependencies")
    print("2. Each task is idempotent and retryable")
    print("3. Track lineage: trace any output back to its source")
    print("4. Validate data between stages (fail fast)")
    print("5. Monitor task durations and record counts as SLIs")
    print("6. Separate extraction from transformation (E, T, L)")
    print("7. Use scheduling + alerting for production pipelines")


if __name__ == "__main__":
    main()
