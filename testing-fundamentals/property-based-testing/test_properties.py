"""
Demo 04 - Property-Based Testing with Hypothesis
==================================================
Use Hypothesis to find edge cases humans would miss.

Instructor talking points:
- Define properties (invariants) that must always hold
- Hypothesis generates random inputs to break your code
- Failing cases are automatically shrunk to minimal examples
- Great for serialization roundtrips, math properties, parsers

Run: pytest -v test_properties.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
from hypothesis import given, assume, settings, example
from hypothesis import strategies as st


# ============================================================================
# Production code: Encoder/Decoder and utility functions
# ============================================================================

def encode(text: str) -> str:
    """Simple run-length encoding: 'aaabbc' -> '3:a,2:b,1:c'.

    Uses delimiters so digit and Unicode characters in the payload
    don't collide with the count prefix.
    """
    if not text:
        return ""
    result = []
    count = 1
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            result.append(f"{count}:{text[i - 1]}")
            count = 1
    result.append(f"{count}:{text[-1]}")
    return ",".join(result)


def decode(encoded: str) -> str:
    """Decode run-length encoding: '3:a,2:b,1:c' -> 'aaabbc'."""
    if not encoded:
        return ""
    result = []
    for part in encoded.split(","):
        count_str, char = part.split(":", 1)
        result.append(char * int(count_str))
    return "".join(result)


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value to [low, high] range."""
    return max(low, min(high, value))


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """Merge two sorted lists into a single sorted list."""
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


@dataclass
class UserProfile:
    name: str
    age: int
    tags: list[str]

    def to_dict(self) -> dict:
        return {"name": self.name, "age": self.age, "tags": self.tags}

    @classmethod
    def from_dict(cls, d: dict) -> UserProfile:
        return cls(name=d["name"], age=d["age"], tags=d["tags"])


# ============================================================================
# Property-Based Tests
# ============================================================================

class TestRoundtripEncoding:
    """Property: encode then decode should return the original string."""

    @given(st.text(alphabet=st.characters(whitelist_categories=("L", "N")), min_size=0, max_size=50))
    def test_encode_decode_roundtrip(self, text):
        """For any text of letters/digits, decode(encode(text)) == text."""
        assume(len(text) > 0)  # Skip empty (handled separately)
        assert decode(encode(text)) == text

    def test_empty_string_roundtrip(self):
        assert decode(encode("")) == ""

    @example("aaa")
    @example("abc")
    @example("aabbbcccc")
    @given(st.text(alphabet="abc", min_size=1, max_size=20))
    def test_encoded_is_shorter_or_equal_for_runs(self, text):
        """Encoded form should not be longer than naive representation for repeated chars."""
        encoded = encode(text)
        # For single chars, encoding adds a digit prefix, so it can be longer.
        # But for runs of 3+, it should be shorter.
        if all(c == text[0] for c in text) and len(text) >= 3:
            assert len(encoded) <= len(text)


class TestClamp:
    """Properties of the clamp function."""

    @given(st.floats(allow_nan=False), st.floats(allow_nan=False), st.floats(allow_nan=False))
    def test_clamp_result_within_bounds(self, value, low, high):
        """Clamped value is always within [low, high]."""
        assume(low <= high)
        result = clamp(value, low, high)
        assert low <= result <= high

    @given(st.floats(min_value=-1000, max_value=1000, allow_nan=False))
    def test_clamp_value_in_range_unchanged(self, value):
        """If value is already in range, clamp returns it unchanged."""
        assert clamp(value, -1000, 1000) == value

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_clamp_idempotent(self, value):
        """Clamping twice gives same result as once."""
        first = clamp(value, 0, 100)
        second = clamp(first, 0, 100)
        assert first == second


class TestMergeSorted:
    """Properties of merge sort."""

    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_merge_produces_sorted_output(self, a, b):
        """Merged output of two sorted lists is always sorted."""
        a_sorted = sorted(a)
        b_sorted = sorted(b)
        result = merge_sorted(a_sorted, b_sorted)
        assert result == sorted(result)

    @given(st.lists(st.integers()), st.lists(st.integers()))
    def test_merge_preserves_all_elements(self, a, b):
        """All elements from both inputs appear in output."""
        a_sorted = sorted(a)
        b_sorted = sorted(b)
        result = merge_sorted(a_sorted, b_sorted)
        assert len(result) == len(a) + len(b)
        assert sorted(result) == sorted(a + b)

    @given(st.lists(st.integers()))
    def test_merge_with_empty_returns_original(self, a):
        """Merging with empty list returns the original."""
        a_sorted = sorted(a)
        assert merge_sorted(a_sorted, []) == a_sorted
        assert merge_sorted([], a_sorted) == a_sorted


class TestUserProfileSerialization:
    """Property: serialization roundtrip preserves data."""

    @given(
        st.text(min_size=1, max_size=50),
        st.integers(min_value=0, max_value=150),
        st.lists(st.text(min_size=1, max_size=20), max_size=10),
    )
    def test_dict_roundtrip(self, name, age, tags):
        """UserProfile -> dict -> UserProfile preserves all fields."""
        original = UserProfile(name=name, age=age, tags=tags)
        restored = UserProfile.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.age == original.age
        assert restored.tags == original.tags

    @given(
        st.text(min_size=1, max_size=50),
        st.integers(min_value=0, max_value=150),
        st.lists(st.text(min_size=1, max_size=20), max_size=10),
    )
    def test_json_roundtrip(self, name, age, tags):
        """UserProfile -> JSON -> UserProfile preserves all fields."""
        original = UserProfile(name=name, age=age, tags=tags)
        json_str = json.dumps(original.to_dict())
        restored = UserProfile.from_dict(json.loads(json_str))
        assert restored == original


# ============================================================================
# Commutative / Associative properties
# ============================================================================

class TestMathProperties:
    """Demonstrate fundamental algebraic properties."""

    @given(st.integers(), st.integers())
    def test_addition_is_commutative(self, a, b):
        assert a + b == b + a

    @given(st.integers(), st.integers(), st.integers())
    def test_addition_is_associative(self, a, b, c):
        assert (a + b) + c == a + (b + c)

    @given(st.lists(st.integers()))
    def test_sorted_is_idempotent(self, lst):
        """Sorting twice gives same result as sorting once."""
        assert sorted(sorted(lst)) == sorted(lst)

    @given(st.lists(st.integers()))
    def test_reverse_reverse_is_identity(self, lst):
        """Reversing a list twice returns the original."""
        assert list(reversed(list(reversed(lst)))) == lst
