# Engineering Specification and Operational Manual

**Project Identifier:** User Database RESTful Application Interface  
**System Core:** FastAPI / SQLAlchemy ORM / SQLite DB  
**Version:** 0.1.0  
**Target Environment:** Production / Staging

---

## 1. System Overview and Architecture

This service provides a standardized, high-performance RESTful API designed to execute Create, Read, Update, and Delete (CRUD) operations against an underlying relational database layer.

The architecture utilizes a declarative data layer coupled with schema reflection to interface with pre-existing database structures without code-level duplication.

### Key Technical Parameters

- **High-Performance Routing:** Asynchronous endpoint execution via FastAPI.
- **Relational Mapping:** SQLAlchemy Object-Relational Mapper (ORM).
- **Dynamic Schema Mapping:** Runtime reflection using the `autoload_with` protocol.
- **Strict Type Assertion:** Data parsing and validation via Pydantic.

---

## 2. Architectural Hardening and Security

To ensure structural integrity and mitigate operational risk, the application implements layers of operational hardening.

### A. Rate Limiting Middleware

- **Mechanics:** Per-client in-memory sliding window evaluated per request.
- **Threshold:** Maximum of 100 requests per 60-second operational window.
- **Enforcement:** Exceeded limits trigger immediate termination of the request lifecycle, returning **HTTP 429 (Too Many Requests)**.

### B. Atomic Transaction Isolation

- Engine interactions are isolated via contextual session states.
- Database failures are prevented from corrupting persisted state by relying on SQLAlchemy transactional semantics.

### C. Centralized Exception Handling

- Runtime exceptions are intercepted at the root boundary by a global handler.
- Detailed stack traces are redirected to secure system logs.
- The public-facing presentation layer safely exposes no architectural details, returning a generic **HTTP 500 (Internal Server Error)**.

---

## 3. System Requirements and Initialization

### Minimum Interpreter Level

- Python 3.10 or higher

### System Dependencies

The deployment workspace maps dependencies deterministically through:

- `pyproject.toml`
- `uv.lock`

### Critical Deployment Prerequisite

The validation schema utilizes advanced regex pattern matching for email fields.

The system environment must have the `email-validator` package successfully installed prior to application execution.

### Environment Synchronization

```bash
uv sync
```

### Application Server Instantiation

Execute the ASGI server wrapper from the repository root:

```bash
uvicorn main:app --reload
```

### Exposed Network Interfaces

- **Swagger UI Documentation:** <http://127.0.0.1:8000/docs>
- **OpenAPI JSON Schema:** <http://127.0.0.1:8000/openapi.json>

---

## 4. Database Matrix Schema Specification

### Persistent Storage

- **Database Engine:** SQLite
- **Database File:** `user_data.db`
- **Table Name:** `user_data`

### Schema Composition

| Column       | Type       | Constraints                          |
| ------------ | ---------- | ------------------------------------ |
| `id`         | BigInteger | Primary Key, Auto-increment, Indexed |
| `first_name` | String     | Max 50 characters, Not Null          |
| `last_name`  | String     | Max 50 characters, Not Null          |
| `email`      | String     | Email syntax validated, Nullable     |
| `gender`     | String     | Must be `"Male"` or `"Female"`       |
| `country`    | String     | Max 30 characters, Not Null          |

### Operational Constraint Notice

Because the data model utilizes runtime reflection (`autoload_with`), the database file and target relational schema must physically exist before the ASGI application initializes.

Failure to ensure this state will induce a fatal `NoSuchTableError` during startup.

---

## 5. Application Programming Interface (API) Specification

### 5.1 Retrieve All Active Records

- **Route:** `GET /users`
- **Access Type:** Public
- **Response:** `Array[UserResponse]`

#### Example

```bash
curl http://127.0.0.1:8000/users
```

---

### 5.2 Retrieve Specific Record by Unique Identifier

- **Route:** `GET /users/get-user/{user_id}`
- **Access Type:** Public
- **Response:** `UserResponse`
- **Success Status:** `HTTP 200`

#### Example

```bash
curl http://127.0.0.1:8000/users/get-user/1
```

#### Error Response

```json
{
  "detail": "User not found"
}
```

**Status:** `HTTP 404`

---

### 5.3 Introduce New Record

- **Route:** `POST /users/create`
- **Access Type:** Public
- **Request Body:** `UserCreate`
- **Response:** `UserResponse`
- **Success Status:** `HTTP 201 Created`

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

### 5.4 Mutate Existing Record Attributes (Partial Modification)

- **Route:** `PUT /users/update/{user_id}`
- **Access Type:** Public
- **Request Body:** `UserUpdate`
- **Response:** `UserResponse`
- **Success Status:** `HTTP 200`

#### Operational Logic

Only fields explicitly supplied in the request payload are modified.

Unspecified attributes remain unchanged.

#### Example Payload

```json
{
  "first_name": "Johnny",
  "email": "johnny.dev@example.com"
}
```

---

### 5.5 Purge System Record

- **Route:** `DELETE /users/delete/{user_id}`
- **Access Type:** Public
- **Response:** `UserResponse | null`
- **Success Status:** `HTTP 200`

#### Example

```bash
curl -X DELETE http://127.0.0.1:8000/users/delete/1
```

#### Operational Logic

- **Record Exists:** Deletes the entry and returns the deleted record payload.
- **Record Missing:** Returns JSON `null` to maintain backend type stability.

---

## 6. Component Blueprint Map

| File           | Responsibility                                                                    |
| -------------- | --------------------------------------------------------------------------------- |
| `main.py`      | Routing, initialization, middleware runtime throttling, and global error handling |
| `models.py`    | ORM engine setup, table reflection, and Pydantic schema definitions               |
| `helper.py`    | Query management, patch logic, and exception handling utilities                   |
| `user_data.db` | Active SQLite database file                                                       |

---

**End of Specification Document**
