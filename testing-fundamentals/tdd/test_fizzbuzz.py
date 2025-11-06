from __future__ import annotations

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "fizzbuzz.py"
spec = spec_from_file_location("fizzbuzz", SRC)
assert spec and spec.loader
mod = module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[attr-defined]
fizzbuzz = mod.fizzbuzz


def test_fizzbuzz_multiples_of_3():
    assert fizzbuzz(3) == "Fizz"
    assert fizzbuzz(6) == "Fizz"


def test_fizzbuzz_multiples_of_5():
    assert fizzbuzz(5) == "Buzz"
    assert fizzbuzz(10) == "Buzz"


def test_fizzbuzz_multiples_of_15():
    assert fizzbuzz(15) == "FizzBuzz"


def test_fizzbuzz_other_numbers():
    assert fizzbuzz(1) == "1"
    assert fizzbuzz(2) == "2"
