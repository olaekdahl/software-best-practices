from __future__ import annotations

import argparse
import json
from pydantic import BaseModel, ValidationError, EmailStr


class User(BaseModel):
    username: str
    email: EmailStr


def load_json_validated(path: str) -> User:
    data = json.loads(open(path, "r", encoding="utf-8").read())
    return User.model_validate(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    try:
        user = load_json_validated(args.json)
        print("Loaded valid user:", user.model_dump())
    except (json.JSONDecodeError, ValidationError) as e:
        print("Rejected invalid input:", e)


if __name__ == "__main__":
    main()
