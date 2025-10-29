from typing import Optional,List
from sqlmodel import Field, SQLModel, Relationship

class Type(SQLModel, table = True):
    __tablename__ = "types"
    id: Optional[int] = Field(default = None, primary_key = True)
    name: str = Field(default = None)
    
    vms: List["Vm"] = Relationship(back_populates = "vm_type")