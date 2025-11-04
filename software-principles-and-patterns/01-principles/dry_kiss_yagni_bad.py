# DRY/KISS/YAGNI (bad): duplicated validation and unnecessary complexity
# Talking points:
# - Same regex copy-pasted (DRY violation).
# - Two identical helpers add noise (KISS violation).
# - Don’t split until needs diverge (YAGNI).
#
# Problems:
# - DRY: Same regex copy-pasted; one will drift when requirements change.
# - KISS: Two functions with identical behavior add cognitive load.
# - YAGNI: Until roles diverge, keep one simple helper.
import re


def user_email_valid(email: str) -> bool:
    # duplicated regex everywhere
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def admin_email_valid(email: str) -> bool:
    # duplicated regex again (DRY violation)
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def main() -> None:
    users = ["user@example.com", "bad"]
    for u in users:
        print(u, user_email_valid(u), admin_email_valid(u))


if __name__ == "__main__":
    main()
