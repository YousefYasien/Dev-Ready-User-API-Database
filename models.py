from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import create_engine, Column, BigInteger
from sqlalchemy.orm import declarative_base

engine = create_engine(
    'sqlite:///user_data.db',
    echo=True,
    connect_args={"check_same_thread": False}  # Crucial for multi-threaded FastAPI execution
)

Base = declarative_base()


# 2. Database Model Reflection Mapping
class user_data(Base):
    __tablename__ = 'user_data'

    # Explicitly declaring the PK is clean, but tell reflection it's okay to overlay
    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)

    __table_args__ = {
        'autoload_with': engine,
        'extend_existing': True  # Safe overlay validation override
    }


# 3. Clean Pydantic Composition Architecture (No Multi-Class Inheritance)
class UserBase(BaseModel):
    first_name: str = Field(..., max_length=50, description='First Name Of the User')
    last_name: str = Field(..., max_length=50, description='Last Name Of the User')
    email: Optional[EmailStr] = Field(None, description='Email Address Of the User')
    gender: Literal['Male', 'Female']
    country: str = Field(..., max_length=30, description='Country Of the User')


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    # Modern Pydantic V2 configuration block
    model_config = ConfigDict(from_attributes=True)


class DeleteUserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    # Every parameter is completely optional to allow partial PATCH/PUT mutations
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    gender: Optional[Literal['Male', 'Female']] = None
    country: Optional[str] = Field(None, max_length=30)
