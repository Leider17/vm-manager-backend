
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class UserBase(SQLModel):
    name: str = Field(default = None)
    email: str = Field(default = None, unique = True) 
    password: str = Field(default = None)
    

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    email: str
    password: str

class userResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: userResponse
    

