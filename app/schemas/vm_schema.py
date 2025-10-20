
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class VmBase(SQLModel):
    name: str = Field(min_length = 5, max_length = 30)
    vnc_port: int =  Field(min_length = 5, max_length = 30)
    state: str = Field(min_length = 5, max_length = 30)
    user_id: int = Field(default = None, foreign_key = "users.id")
    type_id: int = Field(default = None, foreign_key = "types.id")


class VmCreate(VmBase):
    pass

class VmUpdate(VmBase):
    pass

class provisionRequest(BaseModel):
    UserId: int
    vmType: str