# Security by Design

Practical, bite-sized Python demos for building secure software by default. Each example shows a risky pattern and a safer alternative you can copy into real code.

## Topics covered

- Secure coding practices
  - Least privilege, no hard-coded secrets, safe error handling
- Common vulnerabilities (OWASP Top 10)
  - SQL injection, XSS, insecure deserialization and mitigations
- Input validation
  - Sanitize and validate all external input
- Authentication and authorization basics
  - Strong password hashing and role-based access control (RBAC)

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r security-by-design/requirements.txt

# Run the demo API (XSS safe/unsafe, login, RBAC, search safe/unsafe)
make -C security-by-design run-api
# Then visit:
#  - http://127.0.0.1:8000/greet-vuln?name=<script>alert(1)</script>
#  - http://127.0.0.1:8000/greet-safe?name=<script>alert(1)</script>
#  - POST http://127.0.0.1:8000/login {"username":"admin","password":"admin123"}
#  - GET  http://127.0.0.1:8000/admin/dashboard  with Authorization: Bearer <token>

# SQL injection demos (console)
make -C security-by-design demo-sql-vuln
make -C security-by-design demo-sql-safe

# Deserialization demos
make -C security-by-design demo-deser-insecure
make -C security-by-design demo-deser-safe

# Input validation demo
make -C security-by-design demo-validate
```

## Folder layout

- `src/app.py` – FastAPI app with XSS safe/unsafe, login, and RBAC-protected endpoint; SQL search safe/unsafe
- `src/config_insecure.py` vs `src/config_secure.py` – secrets and error handling patterns
- `src/sql_injection_vulnerable.py` and `src/sql_injection_safe.py` – SQLite demos
- `src/insecure_deserialization.py` and `src/safe_deserialization.py` – pickle vs JSON+pydantic
- `src/input_validation.py` – sanitization and validation helpers

## Key practices (cheat sheet)

- Never concatenate SQL—use parameterized queries.
- Escape untrusted output in HTML (or rely on templating that escapes by default).
- Don’t use pickle on untrusted data; prefer JSON + schema validation.
- Don’t hard-code secrets; read from environment/secret store; fail closed if missing.
- Hash passwords with a strong algorithm (bcrypt/argon2) and use RBAC checks at the boundary.
- Validate every external input (length, type, allow-list) and normalize before use.