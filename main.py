import logging
import time
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from helper import apply_updates, commit_and_refresh, get_user_or_404
from models import DeleteUserResponse, UserCreate, UserResponse, UserUpdate, engine, user_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User DB API", version="0.1.0")

SessionLocal = sessionmaker(autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# Simple in-memory rate limiter with a structured layout
_REQUEST_LIMIT = 100
_WINDOW_SECONDS = 60
_request_counts: dict[str, tuple[int, float]] = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    count, window_start = _request_counts.get(client_ip, (0, now))

    if now - window_start >= _WINDOW_SECONDS:
        count = 0
        window_start = now

    count += 1

    if count > _REQUEST_LIMIT:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded"},
        )

    _request_counts[client_ip] = (count, window_start)
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error encountered during request execution")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/users", response_model=list[UserResponse])
def get_users(db: db_dependency):
    return db.query(user_data).all()


@app.get("/users/get-user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: db_dependency):
    return get_user_or_404(db, user_data, user_id)


@app.post("/users/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_user(user: UserCreate, db: db_dependency):
    new_user = user_data(**user.model_dump())
    db.add(new_user)

    try:
        commit_and_refresh(db, new_user)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database insertion failure while creating user")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user due to database constraints."
        )

    return new_user


@app.delete("/users/delete/{user_id}", response_model=DeleteUserResponse | None)
def delete_user(user_id: int, db: db_dependency):
    try:
        user_to_delete = get_user_or_404(db, user_data, user_id)
    except HTTPException:
        # Structured semantic preservation: allow return of None without failing validation
        return None

    try:
        to_return = DeleteUserResponse.model_validate(user_to_delete)
        db.delete(user_to_delete)
        db.commit()
        return to_return
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to complete user deletion transaction")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal transaction error occurred."
        )


@app.put("/users/update/{user_id}", response_model=UserResponse)
def update_user(user_id: int, upd_user: UserUpdate, db: db_dependency):
    user = get_user_or_404(db, user_data, user_id)
    apply_updates(user, upd_user)

    try:
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to update attributes for user %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to commit updates."
        )
