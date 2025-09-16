
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class UserBase(SQLModel):
    email: str = Field(default=None,unique=True) 
    password: str = Field(default=None)
    

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class UserId(BaseModel):
    id: int
