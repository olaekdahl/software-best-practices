"""Module with issues for static analysis demonstrations."""

def duplicate_logic(a: int, b: int) -> int:
    # Intentional overly verbose logic; could be simplified
    result = 0
    for value in (a, b):
        result += value
    return result


def dead_code(flag: bool) -> int:
    if flag:
        return 1
    else:
        return 0
    return 999  # unreachable, should be flagged


def broad_except_demo() -> None:
    try:
        int("not-an-int")
    except Exception:  # noqa: BLE001 broad
        pass  # noqa: S110 (bandit) try/except/pass
