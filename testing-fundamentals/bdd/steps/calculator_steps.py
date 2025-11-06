from __future__ import annotations

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src" / "calculator.py"
spec = spec_from_file_location("calculator", SRC)
assert spec and spec.loader
mod = module_from_spec(spec)
spec.loader.exec_module(mod)  # type: ignore[attr-defined]
add = mod.add
divide = mod.divide

context = {}


def given_numbers(a: str, b: str) -> None:
    context["a"], context["b"] = float(a), float(b)


def when_add() -> None:
    context["result"] = add(context["a"], context["b"])


def when_divide() -> None:
    try:
        context["result"] = divide(context["a"], context["b"])
        context["error"] = None
    except Exception as e:  # noqa: BLE001
        context["error"] = e


def then_result_is(expected: str) -> None:
    actual = context.get("result")
    assert actual == float(expected), f"Expected {expected}, got {actual}"  # type: ignore[arg-type]


def then_error_is_raised() -> None:
    assert context.get("error") is not None, "Expected an error but none was raised"
