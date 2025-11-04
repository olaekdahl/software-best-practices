# LSP/ISP (good): segregated capabilities and safe substitution
# Talking points:
# - Capability-based protocols (Flyer/Swimmer) align contracts with reality.
# - Safe substitution: only types that can fly implement Flyer.
# - Static typing can flag misuse early.
#
# Approach:
# - Define small capability interfaces (Flyer, Swimmer) instead of a fat base class.
# - Only types that can fly implement Flyer; only swimmers implement Swimmer.
#   Substitution is safe because contracts match reality.
from typing import Protocol


class Flyer(Protocol):
    def fly(self) -> None: ...


class Swimmer(Protocol):
    def swim(self) -> None: ...


class Eagle:
    def fly(self) -> None:
        print("Eagle flying high")


class Penguin:
    def swim(self) -> None:
        print("Penguin swimming fast")


def launch_into_sky(f: Flyer) -> None:
    # Works for any implementor of Flyer, regardless of unrelated abilities
    f.fly()


def send_to_pool(s: Swimmer) -> None:
    # Works for any implementor of Swimmer
    s.swim()


if __name__ == "__main__":
    launch_into_sky(Eagle())         # OK
    send_to_pool(Penguin())          # OK
    # launch_into_sky(Penguin())     # type checkers will flag this; runtime would fail
