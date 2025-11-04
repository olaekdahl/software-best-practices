# DRY/KISS/YAGNI (good): single helper, simple design
# Talking points:
# - One compiled regex reused everywhere (DRY).
# - One helper keeps it simple (KISS).
# - Add more variants only when truly needed (YAGNI).
#
# Approach:
# - One compiled regex reused everywhere (DRY).
# - One helper function keeps the surface area minimal (KISS).
# - If future roles need different rules, add them then (YAGNI).
import re
_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email_valid(email: str) -> bool:
    # Reuse a single compiled pattern for performance and consistency
    return bool(_re.match(email))


def main() -> None:
    for u in ["user@example.com", "bad"]:
        print(u, email_valid(u))


if __name__ == "__main__":
    main()
