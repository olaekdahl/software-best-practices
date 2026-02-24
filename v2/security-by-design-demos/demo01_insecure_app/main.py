"""
Demo 01 - Insecure App (Anti-patterns)
========================================
Intentionally INSECURE code showing common vulnerabilities.

Instructor talking points:
- SQL injection via string concatenation
- Hardcoded secrets in source code
- No input validation or sanitization
- Plaintext password storage
- Overly permissive error messages leaking internals
- No rate limiting or access control

WARNING: This code is intentionally vulnerable for educational purposes.
Never use these patterns in production.

Run: python main.py
"""

import sqlite3
import os


# VULNERABILITY 1: Hardcoded secret in source code
API_KEY = "sk-prod-abc123xyz789secretkey"
DATABASE_PASSWORD = "admin123!"
JWT_SECRET = "super-secret-jwt-key-do-not-share"


def create_database():
    """Create a sample database with users."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT
        )
    """)
    # VULNERABILITY 2: Plaintext passwords stored in database
    cursor.executemany(
        "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
        [
            ("admin", "admin123", "admin@company.com", "admin"),
            ("alice", "password123", "alice@company.com", "user"),
            ("bob", "bob2025", "bob@company.com", "user"),
        ],
    )
    conn.commit()
    return conn


def login_insecure(conn, username, password):
    """VULNERABILITY 3: SQL injection via string concatenation.

    An attacker can input: username = ' OR '1'='1' --
    """
    cursor = conn.cursor()
    # BAD: String concatenation allows SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"  Executing query: {query}")
    cursor.execute(query)
    user = cursor.fetchone()
    if user:
        print(f"  Login successful! User: {user[1]}, Role: {user[4]}")
        return user
    else:
        print("  Login failed!")
        return None


def search_users_insecure(conn, search_term):
    """VULNERABILITY 4: SQL injection in search."""
    cursor = conn.cursor()
    # BAD: String formatting in SQL
    query = f"SELECT username, email FROM users WHERE username LIKE '%{search_term}%'"
    print(f"  Executing query: {query}")
    cursor.execute(query)
    return cursor.fetchall()


def get_user_insecure(conn, user_id):
    """VULNERABILITY 5: Leaking internal details in errors."""
    cursor = conn.cursor()
    try:
        # BAD: String formatting
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        user = cursor.fetchone()
        if not user:
            # BAD: Leaking database structure in error message
            raise Exception(
                f"User not found in table 'users' (columns: id, username, "
                f"password, email, role) for id={user_id}"
            )
        return user
    except Exception as e:
        # BAD: Returning full exception details to user
        print(f"  Error: {e}")
        return None


def render_greeting_insecure(username):
    """VULNERABILITY 6: No output encoding (XSS potential).

    If username contains <script>alert('xss')</script>, it would execute
    in a web context.
    """
    # BAD: No HTML encoding
    return f"<h1>Welcome, {username}!</h1>"


def process_file_insecure(filename):
    """VULNERABILITY 7: Path traversal.

    Attacker can input: ../../etc/passwd
    """
    # BAD: No path validation
    filepath = f"/uploads/{filename}"
    print(f"  Processing file: {filepath}")
    return filepath


def main():
    print("=== Demo: Insecure App (Anti-patterns) ===\n")
    conn = create_database()

    # --- Normal login ---
    print("--- Normal Login ---")
    login_insecure(conn, "alice", "password123")
    print()

    # --- SQL Injection Attack ---
    print("--- SQL Injection Attack ---")
    login_insecure(conn, "' OR '1'='1' --", "anything")
    print()

    # --- Search SQL Injection ---
    print("--- Search SQL Injection ---")
    results = search_users_insecure(conn, "' UNION SELECT password, email FROM users --")
    print(f"  Results: {results}")
    print()

    # --- Error message leaking internals ---
    print("--- Error Leaking Internals ---")
    get_user_insecure(conn, "999 OR 1=1")
    print()

    # --- XSS potential ---
    print("--- XSS Potential ---")
    html = render_greeting_insecure("<script>alert('xss')</script>")
    print(f"  Generated HTML: {html}")
    print()

    # --- Path traversal ---
    print("--- Path Traversal ---")
    process_file_insecure("../../etc/passwd")
    print()

    # --- Hardcoded secrets ---
    print("--- Hardcoded Secrets ---")
    print(f"  API Key in source: {API_KEY}")
    print(f"  DB Password in source: {DATABASE_PASSWORD}")

    print("\n--- Vulnerabilities Found ---")
    print("1. Hardcoded secrets in source code")
    print("2. Plaintext password storage")
    print("3. SQL injection via string concatenation")
    print("4. SQL injection in search queries")
    print("5. Internal details leaked in error messages")
    print("6. No output encoding (XSS risk)")
    print("7. Path traversal in file handling")
    print("8. No rate limiting or access control")

    conn.close()


if __name__ == "__main__":
    main()
