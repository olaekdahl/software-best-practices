# Security by Design - Demos

Progressive demos from insecure code to a hardened application.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_insecure_app | Common vulnerabilities (SQL injection, hardcoded secrets) | Naive |
| demo02_input_validation | Input validation, parameterized queries, output encoding | Intermediate |
| demo03_auth_jwt | JWT authentication with RBAC | Intermediate |
| demo04_secrets_management | Environment-based secrets with rotation | Advanced |
| demo05_secure_pipeline | SAST, SCA, secret scanning in CI | Real-world |

## Setup

```bash
pip install pyjwt cryptography
```

## Running

```bash
cd demo01_insecure_app
python main.py
```
