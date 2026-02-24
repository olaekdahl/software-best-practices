"""
Demo 03 - Data Contracts and Schema Validation
=================================================
Validates data against contracts before processing.

Instructor talking points:
- Data contracts define the expected shape of data
- Validate at boundaries (ingestion, between stages)
- Schema evolution: backward and forward compatibility
- Great Expectations-style checks (custom rules)
- Fail fast on contract violations

Run: python main.py
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable


# ============================================================================
# Data contract definition
# ============================================================================

class FieldType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DATE = "date"       # YYYY-MM-DD
    BOOLEAN = "boolean"
    ENUM = "enum"


@dataclass
class FieldConstraint:
    """Constraints for a single field in a data contract."""
    name: str
    field_type: FieldType
    required: bool = True
    nullable: bool = False
    min_value: float | None = None
    max_value: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    allowed_values: list[str] | None = None
    description: str = ""


@dataclass
class DataContract:
    """A data contract defining expected schema and quality rules."""
    name: str
    version: str
    owner: str
    description: str
    fields: list[FieldConstraint] = field(default_factory=list)
    custom_rules: list[Callable] = field(default_factory=list)

    def to_json_schema(self) -> dict:
        """Convert to JSON Schema format."""
        properties = {}
        required = []

        for f in self.fields:
            prop: dict[str, Any] = {"description": f.description}

            if f.field_type == FieldType.STRING:
                prop["type"] = "string"
                if f.min_length:
                    prop["minLength"] = f.min_length
                if f.max_length:
                    prop["maxLength"] = f.max_length
                if f.pattern:
                    prop["pattern"] = f.pattern
            elif f.field_type == FieldType.INTEGER:
                prop["type"] = "integer"
                if f.min_value is not None:
                    prop["minimum"] = int(f.min_value)
                if f.max_value is not None:
                    prop["maximum"] = int(f.max_value)
            elif f.field_type == FieldType.FLOAT:
                prop["type"] = "number"
                if f.min_value is not None:
                    prop["minimum"] = f.min_value
                if f.max_value is not None:
                    prop["maximum"] = f.max_value
            elif f.field_type == FieldType.DATE:
                prop["type"] = "string"
                prop["format"] = "date"
                prop["pattern"] = r"^\d{4}-\d{2}-\d{2}$"
            elif f.field_type == FieldType.BOOLEAN:
                prop["type"] = "boolean"
            elif f.field_type == FieldType.ENUM:
                prop["type"] = "string"
                if f.allowed_values:
                    prop["enum"] = f.allowed_values

            properties[f.name] = prop
            if f.required:
                required.append(f.name)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": self.name,
            "description": self.description,
            "type": "object",
            "properties": properties,
            "required": required,
        }


# ============================================================================
# Validator
# ============================================================================

@dataclass
class ValidationError:
    """A single validation error."""
    row_index: int
    field: str
    rule: str
    value: Any
    message: str


@dataclass
class ValidationResult:
    """Result of validating a dataset against a contract."""
    contract: str
    total_rows: int
    valid_rows: int = 0
    invalid_rows: int = 0
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.invalid_rows == 0

    @property
    def error_rate(self) -> float:
        if self.total_rows == 0:
            return 0.0
        return self.invalid_rows / self.total_rows


class ContractValidator:
    """Validates data against a data contract."""

    def __init__(self, contract: DataContract):
        self.contract = contract
        self._field_map = {f.name: f for f in contract.fields}

    def validate_dataset(self, rows: list[dict]) -> ValidationResult:
        """Validate an entire dataset against the contract."""
        result = ValidationResult(
            contract=self.contract.name,
            total_rows=len(rows),
        )

        for i, row in enumerate(rows):
            row_errors = self._validate_row(i, row)
            if row_errors:
                result.invalid_rows += 1
                result.errors.extend(row_errors)
            else:
                result.valid_rows += 1

        # Run custom rules
        for rule_fn in self.contract.custom_rules:
            custom_errors = rule_fn(rows)
            result.errors.extend(custom_errors)
            if custom_errors:
                # Custom rules may invalidate rows not caught by field checks
                result.invalid_rows += len(set(e.row_index for e in custom_errors) -
                                           set(e.row_index for e in result.errors[:-len(custom_errors)]))

        return result

    def _validate_row(self, index: int, row: dict) -> list[ValidationError]:
        """Validate a single row."""
        errors = []

        for constraint in self.contract.fields:
            value = row.get(constraint.name)

            # Required check
            if constraint.required and (value is None or value == ""):
                errors.append(ValidationError(
                    index, constraint.name, "required",
                    value, f"Field '{constraint.name}' is required"
                ))
                continue

            if value is None or value == "":
                continue

            # Type checks
            if constraint.field_type == FieldType.INTEGER:
                try:
                    int_val = int(value)
                    if constraint.min_value is not None and int_val < constraint.min_value:
                        errors.append(ValidationError(
                            index, constraint.name, "min_value",
                            value, f"Value {int_val} < minimum {constraint.min_value}"
                        ))
                    if constraint.max_value is not None and int_val > constraint.max_value:
                        errors.append(ValidationError(
                            index, constraint.name, "max_value",
                            value, f"Value {int_val} > maximum {constraint.max_value}"
                        ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        index, constraint.name, "type",
                        value, f"Expected integer, got '{value}'"
                    ))

            elif constraint.field_type == FieldType.FLOAT:
                try:
                    float_val = float(value)
                    if constraint.min_value is not None and float_val < constraint.min_value:
                        errors.append(ValidationError(
                            index, constraint.name, "min_value",
                            value, f"Value {float_val} < minimum {constraint.min_value}"
                        ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        index, constraint.name, "type",
                        value, f"Expected float, got '{value}'"
                    ))

            elif constraint.field_type == FieldType.DATE:
                try:
                    datetime.strptime(str(value), "%Y-%m-%d")
                except ValueError:
                    errors.append(ValidationError(
                        index, constraint.name, "format",
                        value, f"Expected date YYYY-MM-DD, got '{value}'"
                    ))

            elif constraint.field_type == FieldType.ENUM:
                if constraint.allowed_values and str(value) not in constraint.allowed_values:
                    errors.append(ValidationError(
                        index, constraint.name, "enum",
                        value, f"Value '{value}' not in {constraint.allowed_values}"
                    ))

            # Pattern check
            if constraint.pattern and isinstance(value, str):
                if not re.match(constraint.pattern, value):
                    errors.append(ValidationError(
                        index, constraint.name, "pattern",
                        value, f"Value '{value}' doesn't match pattern '{constraint.pattern}'"
                    ))

        return errors


# ============================================================================
# Define contracts
# ============================================================================

def create_sales_contract() -> DataContract:
    """Define the sales data contract."""

    def check_no_future_dates(rows: list[dict]) -> list[ValidationError]:
        today = datetime.now().strftime("%Y-%m-%d")
        errors = []
        for i, row in enumerate(rows):
            if row.get("date", "") > today:
                errors.append(ValidationError(
                    i, "date", "custom:no_future_dates",
                    row["date"], f"Date {row['date']} is in the future"
                ))
        return errors

    def check_total_consistency(rows: list[dict]) -> list[ValidationError]:
        errors = []
        for i, row in enumerate(rows):
            try:
                expected = int(row["quantity"]) * float(row["unit_price"])
                actual = float(row.get("total", 0))
                if abs(expected - actual) > 0.01:
                    errors.append(ValidationError(
                        i, "total", "custom:total_consistency",
                        actual, f"Total {actual} != qty({row['quantity']}) * price({row['unit_price']}) = {expected}"
                    ))
            except (ValueError, TypeError, KeyError):
                pass
        return errors

    return DataContract(
        name="sales_data_v1",
        version="1.0.0",
        owner="data-engineering-team",
        description="Sales transaction data from point-of-sale systems",
        fields=[
            FieldConstraint("date", FieldType.DATE, required=True,
                            description="Transaction date"),
            FieldConstraint("product_id", FieldType.STRING, required=True,
                            pattern=r"^P\d{3}$",
                            description="Product identifier (P###)"),
            FieldConstraint("product_name", FieldType.STRING, required=True,
                            min_length=1, max_length=100,
                            description="Product display name"),
            FieldConstraint("quantity", FieldType.INTEGER, required=True,
                            min_value=1, max_value=10000,
                            description="Units sold (positive)"),
            FieldConstraint("unit_price", FieldType.FLOAT, required=True,
                            min_value=0.01,
                            description="Price per unit in dollars"),
            FieldConstraint("customer_id", FieldType.STRING, required=True,
                            pattern=r"^C\d{3}$",
                            description="Customer identifier (C###)"),
            FieldConstraint("region", FieldType.ENUM, required=True,
                            allowed_values=["North", "South", "East", "West"],
                            description="Sales region"),
        ],
        custom_rules=[check_no_future_dates, check_total_consistency],
    )


# ============================================================================
# Main
# ============================================================================

def main():
    print("=== Demo: Data Contracts and Validation ===\n")

    # Define the contract
    contract = create_sales_contract()

    print(f"--- Contract: {contract.name} v{contract.version} ---")
    print(f"  Owner: {contract.owner}")
    print(f"  Fields: {len(contract.fields)}")
    print(f"  Custom rules: {len(contract.custom_rules)}")
    print()

    # Generate JSON Schema
    schema = contract.to_json_schema()
    print("--- JSON Schema ---\n")
    schema_json = json.dumps(schema, indent=2)
    for line in schema_json.split("\n")[:20]:
        print(f"  {line}")
    print("  ...")
    print()

    # Validate good data
    print("--- Validating Good Data ---\n")
    good_data = [
        {"date": "2025-01-01", "product_id": "P001", "product_name": "Widget A",
         "quantity": "5", "unit_price": "29.99", "total": "149.95",
         "customer_id": "C100", "region": "North"},
        {"date": "2025-01-02", "product_id": "P002", "product_name": "Widget B",
         "quantity": "3", "unit_price": "49.99", "total": "149.97",
         "customer_id": "C101", "region": "South"},
    ]

    validator = ContractValidator(contract)
    result = validator.validate_dataset(good_data)
    print(f"  Valid: {result.valid_rows}/{result.total_rows}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Status: {'PASS' if result.is_valid else 'FAIL'}")
    print()

    # Validate bad data
    print("--- Validating Bad Data ---\n")
    bad_data = [
        {"date": "2025-01-01", "product_id": "P001", "product_name": "Widget A",
         "quantity": "5", "unit_price": "29.99", "total": "149.95",
         "customer_id": "C100", "region": "North"},
        {"date": "not-a-date", "product_id": "INVALID", "product_name": "",
         "quantity": "-3", "unit_price": "0", "total": "0",
         "customer_id": "", "region": "Mars"},
        {"date": "2025-01-03", "product_id": "P003", "product_name": "Gadget",
         "quantity": "2", "unit_price": "100.00", "total": "999.99",
         "customer_id": "C102", "region": "East"},
    ]

    result = validator.validate_dataset(bad_data)
    print(f"  Valid: {result.valid_rows}/{result.total_rows}")
    print(f"  Invalid: {result.invalid_rows}")
    print(f"  Error rate: {result.error_rate:.0%}")
    print(f"  Status: {'PASS' if result.is_valid else 'FAIL'}")
    print()

    print("  Errors:")
    for err in result.errors:
        print(f"    Row {err.row_index}: [{err.rule}] {err.field} = {err.value!r}")
        print(f"      {err.message}")
    print()

    print("--- Data Contract Best Practices ---")
    print("1. Define contracts at data boundaries (producer/consumer)")
    print("2. Include field types, constraints, and business rules")
    print("3. Generate JSON Schema for tool interoperability")
    print("4. Version contracts (breaking vs non-breaking changes)")
    print("5. Custom rules for cross-field and business logic validation")
    print("6. Fail fast: reject bad data before it enters the pipeline")
    print("7. Track contract violations as SLIs")


if __name__ == "__main__":
    main()
