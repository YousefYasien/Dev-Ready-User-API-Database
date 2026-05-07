from sqlalchemy import create_engine, Column, BigInteger

from sqlalchemy.orm import sessionmaker, Session

from sqlalchemy.ext.declarative import declarative_base

from fastapi import FastAPI, HTTPException, Depends

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


engine = create_engine('sqlite:///user_data.db', echo=False)

session = sessionmaker(autoflush=False, bind=engine)()

Base = declarative_base()


class user_data(Base):
    __tablename__ = 'user_data'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    __table_args__ = {'autoload_with': engine}


def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get('/users')
def get_users(db: Session = Depends(get_db)):
    return db.query(user_data).all()


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    gender: str
    country: str


@app.get('/users/get-user/{user_id}', response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(user_data).filter(user_data.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.first()


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=50, description='First Name Of the User')
    last_name: str = Field(..., max_length=50, description='Last Name Of the User')
    email: Optional[EmailStr]
    gender: Literal['Male', 'Female']
    country: str = Field(..., max_length=30, description='Country Of the User')

    class Config:
        from_attributes = True


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


class DeleteUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr]
    gender: Literal['Male', 'Female']
    country: str

    class Config:
        from_attributes = True


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
