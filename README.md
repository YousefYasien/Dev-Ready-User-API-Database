# 🚀 Quick-Start Guide: User DB REST API (FastAPI + SQLite)

Welcome! This repository hosts a lightning-fast, lightweight API used to manage a database of user profiles.

Think of it as a digital phonebook that software applications can read, write to, update, and clean up in real-time.

It's built using:

- **Python**
- **FastAPI** (for speed)
- **SQLite** (a tiny, zero-config local database file)

---

## 💡 The Cool Stuff (Operational Highlights)

### 🛑 Built-in Speed Bumps (Rate Limiting)

To keep malicious users or broken scripts from overwhelming the server, incoming traffic is limited to:

- **100 requests**
- **Per 60 seconds**
- **Per IP address**

If the limit is exceeded, the API responds with:

```http
429 Too Many Requests
```

### 🧼 Automatic Crash Protection (Global Error Handling)

If something breaks behind the scenes:

- Internal errors are logged privately.
- Users never see stack traces or source code.
- The API returns:

```http
500 Internal Server Error
```

### 🔄 Safety Net Data Saves (Atomic Transactions)

If a database operation fails midway:

- Changes are rolled back automatically.
- No partially written records are saved.
- Database consistency is preserved.

---

## 🛠️ Getting Started in 60 Seconds

### 1. Install Python

Ensure you have:

```text
Python 3.10+
```

### 2. Synchronize Dependencies

Using the modern `uv` package manager:

```bash
uv sync
```

### 3. Start the Development Server

```bash
uvicorn main:app --reload
```

### 4. Open the Interactive API

Once running, visit:

```text
http://127.0.0.1:8000/docs
```

This launches Swagger UI, where you can test every endpoint directly from your browser.

---

## 📊 The Blueprint: What's in the Database?

All information is stored inside:

```text
user_data.db
```

The database contains a table with the following fields:

| Field | Description |
|---------|-------------|
| `id` | Auto-generated unique identifier |
| `first_name` | Maximum 50 characters, required |
| `last_name` | Maximum 50 characters, required |
| `email` | Automatically validated email address |
| `gender` | Must be `"Male"` or `"Female"` |
| `country` | Maximum 30 characters, required |

> ⚠️ **Important**
>
> This application uses **Database Reflection**. The `user_data.db` file and required table must already exist before starting the server.

---

## 📡 The Control Panel: How to Interact with the API

### 1. 📋 Get All Users

Retrieve every user in the database.

```bash
curl http://127.0.0.1:8000/users
```

---

### 2. 🔍 Get One User

Retrieve a specific user by ID.

```bash
curl http://127.0.0.1:8000/users/get-user/1
```

#### Error Response

If the user doesn't exist:

```json
{
  "detail": "User not found"
}
```

Status:

```http
404 Not Found
```

---

### 3. ➕ Create a New User

**Endpoint**

```http
POST /users/create
```

#### Example Payload

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "gender": "Male",
  "country": "USA"
}
```

---

### 4. 📝 Update a User (Partial Edits)

Modify only the supplied fields while leaving all others unchanged.

**Endpoint**

```http
PUT /users/update/1
```

#### Example Payload

```json
{
  "first_name": "Johnny",
  "email": "johnny.dev@example.com"
}
```

---

### 5. ❌ Delete a User

Permanently remove a user from the database.

```bash
curl -X DELETE http://127.0.0.1:8000/users/delete/1
```

#### Behavior

- If the user exists:
  - Deletes the record.
  - Returns the deleted user data.

- If the user does not exist:
  - Returns:

```json
null
```

---

## 🗂️ Project Anatomy: Who Does What?

| File | Role | Description |
|--------|--------|-------------|
| `main.py` | 🧠 The Brains | Handles routing, middleware, and rate limiting |
| `models.py` | 🦴 The Skeleton | Defines schemas and database connections |
| `helper.py` | 💪 The Muscle | Performs CRUD operations and validation logic |
| `user_data.db` | 🏦 The Vault | Physical SQLite database file |

---

# 🚀 Happy Coding & Testing!
