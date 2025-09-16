
from sqlmodel import  Field, Relationship
from typing import Optional
from app.models.user_model import User
from app.schemas.vm_schema import VmBase
    
class Vm(VmBase,table=True):
    __tablename__ = "vms"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    user: Optional[User] = Relationship(back_populates="vms")

    
