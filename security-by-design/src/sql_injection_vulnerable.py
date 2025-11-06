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


def find_user_vulnerable(conn: sqlite3.Connection, username: str):
    # UNSAFE: string concatenation enables SQL injection
    query = f"SELECT id, username, email FROM users WHERE username = '{username}'"
    return conn.execute(query).fetchall()


def demo():
    conn = setup_db()
    print("-- Safe input --")
    print(find_user_vulnerable(conn, "alice"))

    print("\n-- Injection payload --")
    payload = "' OR 1=1 --"
    print(find_user_vulnerable(conn, payload))  # returns all rows!


if __name__ == "__main__":
    demo()
