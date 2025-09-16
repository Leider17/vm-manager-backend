from fastapi import APIRouter, HTTPException, Body
from app.services.novnc_service import start_novnc, stop_novnc

router = APIRouter(
    prefix="/novnc",
    tags=["novnc"]
)

@router.post("/connect")
def connect_vm(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    vnc_port = payload.get("vnc_port")
    if not vm_name or not vnc_port:
        raise HTTPException(status_code=400, detail="vm_name y vncPort requeridos")

    novnc_url = start_novnc(vm_name, vnc_port)
    return {"url": novnc_url}

@router.post("/disconnect")
def disconnect_vm(data: dict):
    vm_name = data.get("vm_name")
    if not vm_name:
        raise HTTPException(status_code=400, detail="Se requiere vm_name")

    stop_novnc(vm_name)
    return {"message": f"Túnel para {vm_name} detenido"}
