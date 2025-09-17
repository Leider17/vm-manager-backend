
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class VmBase(SQLModel):
    name: str = Field(min_length=5, max_length=30)
    vnc_port: int =  Field(min_length=5, max_length=30)
    description: str = Field(min_length=3, max_length=255)
    status: str = Field(min_length=5, max_length=30)
    user_id: int = Field(default=None, foreign_key="users.id")
 

class VmCreate(VmBase):
    pass

class VmUpdate(VmBase):
    pass