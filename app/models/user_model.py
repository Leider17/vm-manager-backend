from typing import Optional,List
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table = True):
    __tablename__ = "users"
    id: Optional[int] = Field(default = None, primary_key = True)
    name: str = Field(default = None)
    email: str = Field(unique = True, index=True)
    role: str = Field(default = "student")
    password: str = Field(default = None)
    
    vms: List["Vm"] = Relationship(back_populates = "user")