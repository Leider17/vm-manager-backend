from fastapi import HTTPException,APIRouter, Body
from app.services.mv_service import provision_vm
from app.schemas.vm_schema import provisionRequest
from app.services.mv_service import start_vm_service, stop_vm_service, destroy_vm_service, get_vms_user_service, get_all_vms_service, get_info_vm_service
from fastapi import Depends
from app.core.db import get_session

router= APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/provision")
async def post_provision(request: provisionRequest):
    vm = provision_vm(request.UserId, request.vmType)
    if vm is None:
        raise HTTPException(status_code=500, detail="Error en el aprovisionamiento de la MV.")
    return vm

@router.post("/start")
async def post_start(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return start_vm_service(vm_name)

@router.post("/stop")
async def post_stop(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return stop_vm_service(vm_name)

@router.post("/destroy")
async def post_destroy(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return destroy_vm_service(vm_name)

@router.get("/{user_id}")
async def get_vms_user(user_id: str, session=Depends(get_session)):
    vm = get_vms_user_service(user_id, session)
    if vm is None:
        raise HTTPException(status_code=500, detail="Error al obtener las MVs del usuario.")
    return vm

@router.get("/all")
async def get_all_vms(session=Depends(get_session)):
    vms = get_all_vms_service(session)
    if vms is None:
        raise HTTPException(status_code=500, detail="Error al obtener las MVs.")
    return vms

@router.get("/info/{vm_name}")
async def get_info_vm(vm_name: str):
    vm = get_info_vm_service(vm_name)
    if vm is None:
        raise HTTPException(status_code=500, detail="Error al obtener la información de la MV.")
    return vm