from sqlalchemy import update
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated

from models import *


app = FastAPI()
session = sessionmaker(autoflush=False, bind=engine)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get('/users')
def get_users(db: db_dependency):
    return db.query(user_data).all()


@app.get('/users/get-user/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(user_data, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post('/users/create', response_model=UserCreate, status_code=201)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = user_data(**user.model_dump())
    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        print(f'DEBUG: {e}')
        raise HTTPException(status_code=400, detail='couldn\'t create user')
    return new_user


@app.delete('/users/delete/{user_id}', response_model=DeleteUserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user_to_delete = db.get(user_data, user_id)
        if user_to_delete:
            to_return = DeleteUserResponse.model_validate(user_to_delete)
            db.delete(user_to_delete)
            db.commit()
            return to_return
        return user_to_delete
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put('/users/update/{user_id}', response_model=UserResponse)
async def update_user(user_id: int, upd_user: UserUpdate, db: db_dependency):
    user = db.get(user_data, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='user not found')
    for key, value in upd_user.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
