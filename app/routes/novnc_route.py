from fastapi import APIRouter, HTTPException, Body, FastAPI, WebSocket
from pydantic import BaseModel
from fastapi import Depends
from app.services.novnc_service import create_session
from app.core.auth import get_current_user
from app.schemas.user_schema import UserBase

router = APIRouter(
    prefix="/novnc",
    tags=["novnc"]
)

class ConnectRequest(BaseModel):
    vm_name: str
    user_id: int

class DisconnectRequest(BaseModel):
    vm_name: str

@router.post("/connect")
def connect_vm(request: ConnectRequest, current_user: UserBase = Depends(get_current_user)):
    try:
        token = create_session(request.user_id,request.vm_name)
        return {"websocket_url": f"ws://localhost:8000/vnc-proxy/{token}"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


