from __future__ import annotations

import html
import sqlite3
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Header, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Local sibling imports (no package context needed)
import auth_rbac


app = FastAPI(title="Security by Design Demo")


# --- seed users ---
if not getattr(app.state, "seeded", False):
    auth_rbac.create_user("admin", "admin123", role="admin")
    auth_rbac.create_user("bob", "bobpassword", role="user")
    app.state.seeded = True


# --- in-memory sqlite for search demos ---
def get_db():
    if not hasattr(app.state, "db"):
        conn = sqlite3.connect(":memory:")
        c = conn.cursor()
        c.execute("CREATE TABLE items(id INTEGER PRIMARY KEY, name TEXT)")
        c.executemany("INSERT INTO items(name) VALUES(?)", [("hammer",), ("screwdriver",), ("hacksaw",)])
        conn.commit()
        app.state.db = conn
    return app.state.db


class LoginForm(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(form: LoginForm):
    if not auth_rbac.verify_password(form.username, form.password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"token": auth_rbac.issue_token(form.username)}


def current_user_role(authorization: Optional[str] = Header(None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    token = authorization.split(" ", 1)[1]
    username = auth_rbac.parse_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="invalid token")
    return auth_rbac._USERS[username]["role"]  # for demo only


@app.get("/admin/dashboard")
def admin_dashboard(role: str = Depends(current_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return {"data": "sensitive admin data"}


@app.get("/greet-vuln")
def greet_vuln(name: str = Query("world")):
    # UNSAFE: unescaped input reflected to HTML; content-type text/html so script executes
    body = f"<html><body><h1>Hello {name}</h1></body></html>"
    return HTMLResponse(content=body)


@app.get("/greet-safe")
def greet_safe(name: str = Query("world")):
    body = f"<html><body><h1>Hello {html.escape(name, quote=True)}</h1></body></html>"
    return HTMLResponse(content=body)


@app.get("/search-vuln")
def search_vuln(q: str):
    # UNSAFE: string concatenation allows injection
    conn = get_db()
    query = f"SELECT id, name FROM items WHERE name LIKE '%{q}%'"
    rows = conn.execute(query).fetchall()
    return {"results": rows}


@app.get("/search-safe")
def search_safe(q: str):
    # SAFE: parameterized
    conn = get_db()
    query = "SELECT id, name FROM items WHERE name LIKE ?"
    rows = conn.execute(query, (f"%{q}%",)).fetchall()
    return {"results": rows}
