# User DB API (FastAPI + SQLite + SQLAlchemy)

A small FastAPI service for managing users stored in a local SQLite database.

## Features

- FastAPI REST API
- SQLAlchemy ORM model backed by SQLite (`user_data.db`)
- Pydantic schemas for request/response validation

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic

## Requirements

- Python 3.10+

## Installation

This repo includes `pyproject.toml` and `uv.lock`. If you use **uv**:

```bash
uv sync
```

## Run the API server

From the project root (`y:/yousef/learning/python/user_db`):

```bash
uvicorn main:app --reload
```

After starting, open:

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

## Database

- SQLite database file: `user_data.db` (project root)
- Table name: `user_data`
- Columns:
  - `id` (BigInteger, primary key, autoincrement)
  - `first_name`
  - `last_name`
  - `email` (optional)
  - `gender` (`Male` or `Female`)
  - `country`

> Implementation note: the SQLAlchemy model is configured with `__table_args__ = {'autoload_with': engine}`.
> That means the table must already exist in the SQLite database.

## API Reference

### 1) List all users

**GET** `/users`

```bash
curl http://127.0.0.1:8000/users
```

### 2) Get a user by id

**GET** `/users/get-user/{user_id}`

```bash
curl http://127.0.0.1:8000/users/get-user/1
```

If the user does not exist, the API returns:

```json
{ "detail": "User not found" }
```

### 3) Create a new user

**POST** `/users/create` (returns `201`)

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

Field rules:

- `first_name`: max length 50
- `last_name`: max length 50
- `email`: optional (must be a valid email if provided)
- `gender`: must be `Male` or `Female`
- `country`: max length 30

### 4) Update a user

**PUT** `/users/update/{user_id}`

Updates only the fields provided in the request body.

Example request:

```json
{
  "first_name": "Johnny",
  "email": "johnny@example.com"
}
```

Updateable fields use the same names as the database columns: `first_name`, `last_name`, `email`, `gender`, `country`.

### 5) Delete a user

**DELETE** `/users/delete/{user_id}`

```bash
curl -X DELETE http://127.0.0.1:8000/users/delete/1
```

- If found: returns the deleted user payload.
- If not found / error: returns a `404` with details.

## Notes / Caveats

- The app uses a simple dependency that opens/closes a SQLAlchemy session.
- The delete endpoint attempts to return the deleted record; if it doesn’t exist, behavior depends on the lookup result.

## Project structure

- `main.py`: FastAPI app + endpoints
- `models.py`: SQLAlchemy ORM model + Pydantic schemas
- `user_data.db`: SQLite database file used at runtime
