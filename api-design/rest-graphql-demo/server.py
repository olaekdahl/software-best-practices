#!/usr/bin/env python3
from typing import List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import strawberry
from strawberry.fastapi import GraphQLRouter


# In-memory data store
BOOKS = [
    {"id": "1", "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": "2", "title": "Design Patterns", "author": "Gamma et al."},
]


def next_id() -> str:
    return str(max(int(b["id"]) for b in BOOKS) + 1) if BOOKS else "1"


# ----- REST (FastAPI) -----
class NewBook(BaseModel):
    title: str
    author: str


app = FastAPI(title="REST vs GraphQL Demo", version="0.2")


@app.get("/", tags=["info"])
def info():
    return {"ok": True, "endpoints": ["/rest/...", "/graphql"]}


@app.get("/rest/books", tags=["rest"])
def list_books():
    return BOOKS


@app.get("/rest/books/{book_id}", tags=["rest"])
def get_book(book_id: str):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="not found")
    return book


@app.post("/rest/books", status_code=201, tags=["rest"])
def create_book(payload: NewBook):
    book = {"id": next_id(), "title": payload.title, "author": payload.author}
    BOOKS.append(book)
    return book


# ----- GraphQL (Strawberry + FastAPI) -----
@strawberry.type
class Book:
    id: str
    title: str
    author: str


@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> List[Book]:
        return [Book(**b) for b in BOOKS]

    @strawberry.field
    def book(self, id: str) -> Optional[Book]:
        b = next((x for x in BOOKS if x["id"] == id), None)
        return Book(**b) if b else None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str) -> Book:
        b = {"id": next_id(), "title": title, "author": author}
        BOOKS.append(b)
        return Book(**b)


schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    # Allow `python3 server.py` to run the app directly
    uvicorn.run("server:app", host="0.0.0.0", port=9000, reload=True)
