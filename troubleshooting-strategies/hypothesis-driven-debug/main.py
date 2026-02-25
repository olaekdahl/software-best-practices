"""
Demo 03 - Hypothesis-Driven Debugging
========================================
Demonstrates the systematic hypothesis-test loop for debugging.

Instructor talking points:
- Observe symptoms (don't jump to solutions)
- Form hypothesis (predict root cause)
- Design a test (prove/disprove)
- Narrow scope with binary search
- Document each step for reproducibility

Run: python main.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


# ============================================================================
# The "mystery" system - an order processing pipeline with intermittent failures
# ============================================================================

@dataclass
class Order:
    id: str
    customer: str
    items: list[str]
    total: float
    discount_code: str | None = None
    status: str = "pending"


class OrderPipeline:
    """Order processing pipeline with a subtle bug.

    The bug: discount codes with mixed case are not
    recognized, causing price miscalculation.

    Additionally: orders with exactly 5 items trigger
    a boundary condition in the batch processor.
    """

    DISCOUNT_CODES = {
        "SAVE10": 0.10,
        "SAVE20": 0.20,
        "VIP50": 0.50,
    }

    def __init__(self):
        self.processed: list[dict] = []
        self.errors: list[dict] = []

    def validate_order(self, order: Order) -> bool:
        """Validate order data."""
        if not order.items:
            self.errors.append({"order": order.id, "error": "empty items"})
            return False
        if order.total <= 0:
            self.errors.append({"order": order.id, "error": "invalid total"})
            return False
        return True

    def apply_discount(self, order: Order) -> float:
        """Apply discount code to order total.

        BUG: Case-sensitive comparison means 'save10' won't match 'SAVE10'.
        """
        if order.discount_code is None:
            return order.total
        # BUG: No .upper() on the discount_code lookup
        rate = self.DISCOUNT_CODES.get(order.discount_code, 0)
        return round(order.total * (1 - rate), 2)

    def process_batch(self, orders: list[Order]) -> list[dict]:
        """Process a batch of orders.

        BUG: Off-by-one with range causes index error on batch size 5.
        """
        results = []
        # BUG: Using <= instead of < causes IndexError on exact batch boundary
        for i in range(0, len(orders)):
            order = orders[i]
            if not self.validate_order(order):
                continue

            final_total = self.apply_discount(order)
            order.status = "processed"
            result = {
                "order_id": order.id,
                "customer": order.customer,
                "original_total": order.total,
                "final_total": final_total,
                "discount_applied": order.total != final_total,
            }
            results.append(result)
            self.processed.append(result)

        return results


# ============================================================================
# Debugging session simulation
# ============================================================================

@dataclass
class Hypothesis:
    """A debugging hypothesis to test."""
    id: int
    description: str
    test: str
    prediction: str
    result: str = ""
    verdict: str = ""  # CONFIRMED or REJECTED


def run_debugging_session():
    """Walk through a hypothesis-driven debugging session."""
    print("=== Hypothesis-Driven Debugging Session ===\n")

    # --- Step 1: Observe the symptom ---
    print("--- Step 1: OBSERVE ---\n")
    pipeline = OrderPipeline()
    orders = [
        Order("ORD-1", "Alice", ["item-a"], 100.0, "SAVE10"),
        Order("ORD-2", "Bob", ["item-b"], 200.0, "save20"),  # Lowercase!
        Order("ORD-3", "Charlie", ["item-c", "item-d"], 150.0, None),
        Order("ORD-4", "Diana", ["item-e"], 300.0, "Save10"),  # Mixed case!
    ]

    results = pipeline.process_batch(orders)
    print("  Processing results:")
    for r in results:
        indicator = " <-- NO DISCOUNT?" if not r["discount_applied"] and r["order_id"] in ("ORD-2", "ORD-4") else ""
        print(f"    {r['order_id']}: ${r['original_total']} -> ${r['final_total']} "
              f"(discount: {r['discount_applied']}){indicator}")

    print()
    print("  SYMPTOM: Orders ORD-2 and ORD-4 should have discounts but don't.")
    print("           ORD-1 with 'SAVE10' works, but 'save20' and 'Save10' don't.")
    print()

    # --- Step 2: Form hypotheses ---
    print("--- Step 2: HYPOTHESIZE ---\n")
    hypotheses = [
        Hypothesis(
            1,
            "Discount codes are case-sensitive",
            "Compare 'SAVE10' vs 'save10' vs 'Save10' in lookup",
            "Only exact uppercase matches will return a discount rate",
        ),
        Hypothesis(
            2,
            "Discount codes have expired or been removed",
            "Check DISCOUNT_CODES dict contents",
            "The codes exist but something prevents matching",
        ),
        Hypothesis(
            3,
            "apply_discount() has a logic error in the calculation",
            "Test with a known-good code to verify math",
            "Math is correct for uppercase codes, wrong for others",
        ),
    ]

    for h in hypotheses:
        print(f"  H{h.id}: {h.description}")
        print(f"      Test: {h.test}")
        print(f"      Prediction: {h.prediction}")
        print()

    # --- Step 3: Test each hypothesis ---
    print("--- Step 3: TEST ---\n")

    # Test H1: Case sensitivity
    print("  Testing H1: Case sensitivity")
    codes_to_test = ["SAVE10", "save10", "Save10", "SAVE20", "save20"]
    for code in codes_to_test:
        rate = OrderPipeline.DISCOUNT_CODES.get(code, 0)
        matched = "MATCH" if rate > 0 else "NO MATCH"
        print(f"    '{code}' -> rate={rate} [{matched}]")

    hypotheses[0].result = "Only exact uppercase codes match"
    hypotheses[0].verdict = "CONFIRMED"
    hypotheses[1].result = "Codes exist in dict, issue is matching"
    hypotheses[1].verdict = "REJECTED"
    hypotheses[2].result = "Math is correct, input matching is the issue"
    hypotheses[2].verdict = "REJECTED"
    print()

    for h in hypotheses:
        marker = ">>>" if h.verdict == "CONFIRMED" else "   "
        print(f"  {marker} H{h.id}: {h.verdict} - {h.result}")
    print()

    # --- Step 4: Identify root cause ---
    print("--- Step 4: ROOT CAUSE ---\n")
    print("  Root cause: apply_discount() does a case-sensitive dict lookup.")
    print("  Line: rate = self.DISCOUNT_CODES.get(order.discount_code, 0)")
    print("  Fix: Normalize to uppercase before lookup.")
    print()

    # --- Step 5: Fix and verify ---
    print("--- Step 5: FIX AND VERIFY ---\n")

    class FixedPipeline(OrderPipeline):
        def apply_discount(self, order: Order) -> float:
            if order.discount_code is None:
                return order.total
            # FIX: Normalize case
            rate = self.DISCOUNT_CODES.get(order.discount_code.upper(), 0)
            return round(order.total * (1 - rate), 2)

    fixed = FixedPipeline()
    results = fixed.process_batch(orders)
    print("  After fix:")
    for r in results:
        print(f"    {r['order_id']}: ${r['original_total']} -> ${r['final_total']} "
              f"(discount: {r['discount_applied']})")
    print()

    # --- Step 6: Write regression test ---
    print("--- Step 6: REGRESSION TEST ---\n")
    print("  def test_discount_case_insensitive():")
    print("      pipeline = FixedPipeline()")
    print("      for code in ['SAVE10', 'save10', 'Save10']:")
    print("          order = Order('test', 'user', ['x'], 100.0, code)")
    print("          result = pipeline.apply_discount(order)")
    print("          assert result == 90.0, f'{code} should give 10% off'")
    print()

    # Verify the test passes
    for code in ["SAVE10", "save10", "Save10"]:
        order = Order("test", "user", ["x"], 100.0, code)
        result = fixed.apply_discount(order)
        status = "PASS" if result == 90.0 else f"FAIL (got {result})"
        print(f"    {code}: {status}")

    print()
    print("--- Debugging Process Summary ---")
    print("1. OBSERVE: Describe symptoms precisely")
    print("2. HYPOTHESIZE: List possible causes, ranked by likelihood")
    print("3. TEST: Design experiment to confirm/reject each hypothesis")
    print("4. ROOT CAUSE: Identify the exact line and condition")
    print("5. FIX: Apply minimal, targeted fix")
    print("6. VERIFY: Write regression test to prevent recurrence")


# ============================================================================
# Main
# ============================================================================

def main():
    run_debugging_session()


if __name__ == "__main__":
    main()
