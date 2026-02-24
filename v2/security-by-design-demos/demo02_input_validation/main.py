"""
Demo 02 - Input Validation and Output Encoding
=================================================
Fixes the vulnerabilities from demo01 with proper validation.

Instructor talking points:
- Parameterized queries prevent SQL injection
- Allowlist validation rejects bad input early
- Output encoding prevents XSS
- Path validation prevents traversal
- Proper error messages hide internals

Run: python main.py
"""

from __future__ import annotations

import html
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


# ============================================================================
# Input validation utilities
# ============================================================================

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg"}


def validate_email(email: str) -> str:
    """Validate and normalize email."""
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValueError("Invalid email format")
    if len(email) > 254:
        raise ValueError("Email too long")
    return email


def validate_username(username: str) -> str:
    """Validate username against allowlist pattern."""
    username = username.strip()
    if not USERNAME_RE.match(username):
        raise ValueError(
            "Username must be 3-30 characters, letters/digits/underscore only"
        )
    return username


def validate_search_term(term: str, max_length: int = 50) -> str:
    """Validate search input."""
    term = term.strip()
    if len(term) > max_length:
        raise ValueError(f"Search term too long (max {max_length})")
    if len(term) < 1:
        raise ValueError("Search term required")
    # Allow only safe characters for search
    if not re.match(r"^[a-zA-Z0-9 _-]+$", term):
        raise ValueError("Search term contains invalid characters")
    return term


def validate_filepath(filename: str, base_dir: str = "/uploads") -> Path:
    """Validate file path to prevent traversal attacks."""
    # Normalize and resolve
    clean_name = PurePosixPath(filename).name  # Strip directory components
    if not clean_name:
        raise ValueError("Invalid filename")

    # Check extension allowlist
    ext = PurePosixPath(clean_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    # Construct safe path
    safe_path = Path(base_dir) / clean_name

    # Verify it stays within base_dir
    if not str(safe_path).startswith(base_dir):
        raise ValueError("Path traversal detected")

    return safe_path


# ============================================================================
# Output encoding
# ============================================================================

def encode_html(text: str) -> str:
    """Encode text for safe HTML output."""
    return html.escape(text, quote=True)


def render_greeting_safe(username: str) -> str:
    """Safe HTML rendering with output encoding."""
    safe_name = encode_html(username)
    return f"<h1>Welcome, {safe_name}!</h1>"


# ============================================================================
# Secure database operations
# ============================================================================

def create_database() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)
    cursor.executemany(
        "INSERT INTO users (username, email, role) VALUES (?, ?, ?)",
        [
            ("admin", "admin@company.com", "admin"),
            ("alice", "alice@company.com", "user"),
            ("bob", "bob@company.com", "user"),
        ],
    )
    conn.commit()
    return conn


def login_secure(conn: sqlite3.Connection, username: str, password: str) -> dict | None:
    """Secure login with parameterized queries.

    Uses parameterized queries to prevent SQL injection.
    """
    try:
        clean_username = validate_username(username)
    except ValueError as e:
        print(f"  Validation error: {e}")
        return None

    cursor = conn.cursor()
    # SECURE: Parameterized query prevents SQL injection
    cursor.execute(
        "SELECT id, username, role FROM users WHERE username = ?",
        (clean_username,),
    )
    user = cursor.fetchone()
    if user:
        # In real code, verify password hash here
        print(f"  Login successful: user={user[1]}, role={user[2]}")
        return {"id": user[0], "username": user[1], "role": user[2]}
    else:
        # SECURE: Generic message - don't reveal if user exists
        print("  Invalid credentials")
        return None


def search_users_secure(
    conn: sqlite3.Connection, search_term: str
) -> list[tuple]:
    """Secure search with validation and parameterized query."""
    try:
        clean_term = validate_search_term(search_term)
    except ValueError as e:
        print(f"  Validation error: {e}")
        return []

    cursor = conn.cursor()
    # SECURE: Parameterized LIKE query
    cursor.execute(
        "SELECT username, email FROM users WHERE username LIKE ?",
        (f"%{clean_term}%",),
    )
    return cursor.fetchall()


def get_user_secure(conn: sqlite3.Connection, user_id: str) -> dict | None:
    """Secure user lookup with proper error handling."""
    # Validate input is a positive integer
    try:
        uid = int(user_id)
        if uid < 1:
            raise ValueError("Invalid ID")
    except (ValueError, TypeError):
        print("  Error: Invalid user ID format")
        return None

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (uid,),
    )
    user = cursor.fetchone()
    if not user:
        # SECURE: Generic error, no internal details
        print("  Error: User not found")
        return None
    return {"id": user[0], "username": user[1], "email": user[2], "role": user[3]}


# ============================================================================
# Main demo
# ============================================================================

def main():
    print("=== Demo: Input Validation and Output Encoding ===\n")
    conn = create_database()

    # --- Secure login ---
    print("--- Secure Login ---")
    login_secure(conn, "alice", "password123")
    print()

    # --- SQL injection attempt blocked ---
    print("--- SQL Injection Attempt (Blocked) ---")
    login_secure(conn, "' OR '1'='1' --", "anything")
    print()

    # --- Secure search ---
    print("--- Secure Search ---")
    results = search_users_secure(conn, "ali")
    print(f"  Results: {results}")
    print()

    # --- Search injection attempt blocked ---
    print("--- Search Injection Attempt (Blocked) ---")
    results = search_users_secure(
        conn, "' UNION SELECT password, email FROM users --"
    )
    print(f"  Results: {results}")
    print()

    # --- Secure error handling ---
    print("--- Secure Error Handling ---")
    get_user_secure(conn, "999 OR 1=1")
    get_user_secure(conn, "1")
    print()

    # --- XSS prevention ---
    print("--- XSS Prevention ---")
    safe_html = render_greeting_safe("<script>alert('xss')</script>")
    print(f"  Safe HTML: {safe_html}")
    print()

    # --- Path traversal prevention ---
    print("--- Path Traversal Prevention ---")
    try:
        validate_filepath("../../etc/passwd")
    except ValueError as e:
        print(f"  Blocked: {e}")
    try:
        safe_path = validate_filepath("report.pdf")
        print(f"  Allowed: {safe_path}")
    except ValueError as e:
        print(f"  Blocked: {e}")

    print("\n--- Security Improvements ---")
    print("1. Parameterized queries prevent SQL injection")
    print("2. Input validation with allowlist patterns")
    print("3. Output encoding prevents XSS")
    print("4. Path validation prevents traversal")
    print("5. Generic error messages hide internals")
    print("6. Input length limits prevent abuse")

    conn.close()


if __name__ == "__main__":
    main()
