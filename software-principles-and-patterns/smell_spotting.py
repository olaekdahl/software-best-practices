# Bad-smell spotting exercise: Identify violations of SOLID and DRY
# Questions:
# - Which responsibilities are mixed?
# - Where is OCP violated?
# - Any hidden dependencies?
# - Any duplication to remove?

import re

class ReportService:
    def generate(self, user_email: str, user_role: str, filters: dict) -> str:
        # validation (SRP violation)
        if not user_email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", user_email):
            raise ValueError("bad email")

        # role check
        if user_role == "admin":
            print("[SEC] admin access granted")
        elif user_role == "manager":
            print("[SEC] manager access granted")
        elif user_role == "viewer":
            print("[SEC] viewer access granted")
        else:  # OCP violation: new roles require modifying here
            print("[SEC] unknown role")

        # report compute (mixed concerns)
        result = f"report for {user_email} with {filters}"

        # emailing here (tight coupling)
        print(f"[EMAIL] to={user_email} body={result}")
        return result

if __name__ == "__main__":
    ReportService().generate("user@example.com", "manager", {"region": "us"})
