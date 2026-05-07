from sqlalchemy import create_engine, BigInteger, Column
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


engine = create_engine('sqlite:///user_data.db', echo=True, max_overflow=0)

Base = declarative_base()


class user_data(Base):
    __tablename__ = 'user_data'
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    __table_args__ = {'autoload_with': engine}


class userModel:
    id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr]
    gender: str
    country: str


class UserResponse(BaseModel, userModel):
    pass


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=50, description='First Name Of the User')
    last_name: str = Field(..., max_length=50, description='Last Name Of the User')
    email: Optional[EmailStr]
    gender: Literal['Male', 'Female']
    country: str = Field(..., max_length=30, description='Country Of the User')

    class Config:
        from_attributes = True


class DeleteUserResponse(BaseModel, userModel):

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Literal['Male', 'Female']]
    country: Optional[str]
