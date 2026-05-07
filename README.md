# user_db (FastAPI + SQLite + SQLAlchemy)

A small FastAPI service for managing users stored in a local SQLite database.

## What’s included

- **FastAPI** web API
- **SQLAlchemy** ORM model backed by **SQLite** (`user_data.db`)
- **Pydantic** request/response schemas

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## Requirements

- Python 3.10+ (adjust if your environment differs)

## Installation

This repo contains `pyproject.toml` and `uv.lock`, so if you use **uv** you can install dependencies like:

```bash
uv sync
```

(If you prefer pip and you have a requirements file in your workflow, you can use that instead.)

## Run the API server

From the project root (`y:/yousef/learning/python/user_db`):

```bash
uvicorn main:app --reload
```

Then open:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Database

- SQLite database file: **`user_data.db`** (in the project root)
- Table name: **`user_data`**
- Columns:
  - `id` (BigInteger, primary key, autoincrement)
  - `first_name`
  - `last_name`
  - `email` (optional)
  - `gender` (`Male` or `Female`)
  - `country`

> Implementation note: the SQLAlchemy model uses `__table_args__ = {'autoload_with': engine}`.
> That means the table needs to already exist in the SQLite DB.

## API Reference

### 1) List all users

**GET** `/users`

Returns an array of users.

```bash
curl http://127.0.0.1:8000/users
```

### 2) Get a single user by id

**GET** `/users/get-user/{user_id}`

```bash
curl http://127.0.0.1:8000/users/get-user/1
```

If not found, returns **404**:

- `{"detail":"User not found"}`

### 3) Create a new user

**POST** `/users/create` (returns **201**)

Request body:

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "gender": "Male",
  "country": "USA"
}
```

Field rules (from the request schema):

- `first_name`: max length 50
- `last_name`: max length 50
- `email`: optional (must be a valid email if provided)
- `gender`: must be `Male` or `Female`
- `country`: max length 30

### 4) Delete a user

**DELETE** `/users/delete/{user_id}`

```bash
curl -X DELETE http://127.0.0.1:8000/users/delete/1
```

- If found: returns the deleted user payload.
- If not found / error: returns a **404** with details.

## Notes / Caveats

- The app uses a global SQLAlchemy session object (`session = sessionmaker(... )()`). This works for simple demos, but for production you’d typically create a session per request.
- The delete endpoint attempts to return the deleted record; if the record doesn’t exist, it returns the result of the lookup (which may be `null` depending on how SQLAlchemy behaves).

## Project files

- `main.py`: FastAPI app + SQLAlchemy model + endpoints
- `user_data.db`: SQLite database file used at runtime
