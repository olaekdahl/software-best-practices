from __future__ import annotations

import sqlite3
import time


def setup_db():
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute("CREATE TABLE authors(id INTEGER PRIMARY KEY, name TEXT)")
    c.execute("CREATE TABLE books(id INTEGER PRIMARY KEY, author_id INT, title TEXT)")
    authors = [(i, f"Author {i}") for i in range(1, 501)]
    books = []
    for i in range(1, 501):
        for j in range(10):
            books.append((None, i, f"Book {i}-{j}"))
    c.executemany("INSERT INTO authors(id, name) VALUES(?, ?)", authors)
    c.executemany("INSERT INTO books(author_id, title) VALUES(?, ?)", [(a, t) for _, a, t in books])
    conn.commit()
    return conn


def n_plus_one(conn: sqlite3.Connection):
    cur = conn.cursor()
    t0 = time.perf_counter()
    res = []
    for (aid,) in cur.execute("SELECT id FROM authors").fetchall():
        count = cur.execute("SELECT COUNT(*) FROM books WHERE author_id=?", (aid,)).fetchone()[0]
        res.append((aid, count))
    t1 = time.perf_counter()
    print(f"N+1 queries: {t1-t0:.3f}s, rows={len(res)}")


def join_groupby(conn: sqlite3.Connection):
    cur = conn.cursor()
    t0 = time.perf_counter()
    res = cur.execute(
        "SELECT a.id, COUNT(b.id) FROM authors a LEFT JOIN books b ON a.id=b.author_id GROUP BY a.id"
    ).fetchall()
    t1 = time.perf_counter()
    print(f"JOIN+GROUP BY: {t1-t0:.3f}s, rows={len(res)}")


def main():
    print("-- database query tuning --")
    conn = setup_db()
    n_plus_one(conn)
    join_groupby(conn)


if __name__ == "__main__":
    main()
