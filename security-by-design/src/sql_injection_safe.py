from __future__ import annotations

import sqlite3


def setup_db(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)")
    c.executemany(
        "INSERT INTO users(username, email) VALUES(?, ?)",
        [("alice", "alice@example.com"), ("bob", "bob@example.com"), ("admin", "root@example.com")],
    )
    conn.commit()
    return conn


def find_user_safe(conn: sqlite3.Connection, username: str):
    # SAFE: parameterized query avoids injection
    query = "SELECT id, username, email FROM users WHERE username = ?"
    return conn.execute(query, (username,)).fetchall()


def demo():
    conn = setup_db()
    print("-- Safe input --")
    print(find_user_safe(conn, "alice"))

    print("\n-- Injection payload (treated as literal) --")
    payload = "' OR 1=1 --"
    print(find_user_safe(conn, payload))  # returns empty list


if __name__ == "__main__":
    demo()
