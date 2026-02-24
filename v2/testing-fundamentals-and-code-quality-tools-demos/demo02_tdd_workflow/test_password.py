"""
Demo 02 - TDD Workflow: Red-Green-Refactor
=============================================
Walk through TDD building a password validator step by step.

Instructor talking points:
- RED: Write a failing test first
- GREEN: Write minimum code to pass
- REFACTOR: Improve without breaking tests
- Tests drive the design, not the other way around

Run: pytest -v test_password.py
"""

import re


# ============================================================================
# Production code - built incrementally using TDD
# ============================================================================

class PasswordValidator:
    """Validates passwords against configurable rules.

    Built via TDD:
    1. First test: rejects empty passwords -> added length check
    2. Second test: requires minimum length -> added min_length param
    3. Third test: requires uppercase -> added uppercase check
    4. Fourth test: requires digit -> added digit check
    5. Fifth test: requires special char -> added special char check
    6. Refactor: return all violations at once instead of first only
    """

    def __init__(self, min_length: int = 8):
        self.min_length = min_length

    def validate(self, password: str) -> list[str]:
        """Return list of validation errors. Empty list means valid."""
        errors = []

        if len(password) < self.min_length:
            errors.append(f"Must be at least {self.min_length} characters")

        if not any(c.isupper() for c in password):
            errors.append("Must contain at least one uppercase letter")

        if not any(c.isdigit() for c in password):
            errors.append("Must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Must contain at least one special character")

        return errors

    def is_valid(self, password: str) -> bool:
        return len(self.validate(password)) == 0


# ============================================================================
# Tests - written FIRST in TDD (shown in the order they were written)
# ============================================================================

class TestPasswordValidator:
    """Tests written in TDD order: each test drove a code change."""

    def setup_method(self):
        self.validator = PasswordValidator(min_length=8)

    # --- Step 1: RED -> GREEN: Empty password rejected ---
    def test_empty_password_rejected(self):
        errors = self.validator.validate("")
        assert len(errors) > 0
        assert any("8 characters" in e for e in errors)

    # --- Step 2: RED -> GREEN: Short password rejected ---
    def test_short_password_rejected(self):
        errors = self.validator.validate("Ab1!")
        assert any("8 characters" in e for e in errors)

    # --- Step 3: RED -> GREEN: No uppercase rejected ---
    def test_no_uppercase_rejected(self):
        errors = self.validator.validate("abcdefg1!")
        assert any("uppercase" in e for e in errors)

    # --- Step 4: RED -> GREEN: No digit rejected ---
    def test_no_digit_rejected(self):
        errors = self.validator.validate("Abcdefgh!")
        assert any("digit" in e for e in errors)

    # --- Step 5: RED -> GREEN: No special char rejected ---
    def test_no_special_char_rejected(self):
        errors = self.validator.validate("Abcdefg1")
        assert any("special" in e for e in errors)

    # --- Step 6: REFACTOR: Valid password passes all rules ---
    def test_valid_password_accepted(self):
        errors = self.validator.validate("MyP@ss1rd")
        assert errors == []

    # --- Step 7: is_valid convenience method ---
    def test_is_valid_returns_bool(self):
        assert self.validator.is_valid("MyP@ss1rd") is True
        assert self.validator.is_valid("weak") is False

    # --- Step 8: Multiple errors returned at once ---
    def test_multiple_errors_returned(self):
        errors = self.validator.validate("abc")
        assert len(errors) >= 3  # too short, no upper, no digit, no special

    # --- Step 9: Custom min_length ---
    def test_custom_min_length(self):
        v = PasswordValidator(min_length=12)
        errors = v.validate("MyP@ss1rd")  # 9 chars, valid for 8, not 12
        assert any("12 characters" in e for e in errors)
