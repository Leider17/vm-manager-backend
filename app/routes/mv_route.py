from fastapi import HTTPException,APIRouter, Body
from app.models.vm_model import Vm
from app.services.mv_service import provision_vm
from app.schemas.vm_schema import provisionRequest
from app.core.db import get_session
from app.services.mv_service import start_vm_service, stop_vm_service, destroy_vm_service, get_vms_user_service, get_all_vms_service, get_info_vm_service, get_info_host_service, shutdown_vms_user_service, shutdown_all_vms
from fastapi import Depends
from sqlmodel import Session, select
from app.core.db import get_session
from app.core.auth import get_current_user
from app.schemas.user_schema import UserBase

router = APIRouter(
    prefix="/vm",
    tags=["vm"]
)

@router.post("/provision")
async def post_provision(request: provisionRequest, session: Session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vm = provision_vm(request.UserId, request.vmType, session)
    
    if vm is None:
        raise HTTPException(status_code=500, detail="Error en el aprovisionamiento de la MV.")
    return vm

@router.post("/start")
async def post_start(payload: dict = Body(...), session: Session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vm_name = payload.get("vm_name")

    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return start_vm_service(vm_name, session)

@router.post("/stop")
async def post_stop(payload: dict = Body(...), session: Session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vm_name = payload.get("vm_name")

    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return stop_vm_service(vm_name, session)

@router.post("/destroy")
async def post_destroy(payload: dict = Body(...), session: Session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vm_name = payload.get("vm_name")
    vm = session.exec(select(Vm).where(Vm.name == vm_name)).first()
    if not vm_name:
        raise HTTPException(status_code=400, detail="El nombre de la MV es obligatorio.")
    return destroy_vm_service(vm_name, vm.id, session)

@router.get("/all")
async def get_all_vms(session=Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vms = get_all_vms_service(session)

    if vms is None:
        raise HTTPException(status_code=500, detail="Error al obtener las MVs.")
    return vms

@router.get("/infohost")
async def get_info_host( current_user: UserBase = Depends(get_current_user)):
    info = get_info_host_service()
    if info is None:
        raise HTTPException(status_code=500, detail="Error al obtener la información de la MV.")
    return info

@router.get("/info/{vm_name}")
async def get_info_vm(vm_name: str, current_user: UserBase = Depends(get_current_user)):
    vm = get_info_vm_service(vm_name)
    
    if vm is None:
        raise HTTPException(status_code=500, detail="Error al obtener la información de la MV.")
    return vm

@router.post("/shutdown/all/{user_id}")
async def shutdown_user_vms(user_id: str, session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    status = shutdown_vms_user_service(user_id, session)

    if status is None:
        raise HTTPException(status_code=500, detail="Error al deteneter las mvs.")
    return status

@router.post("/shutdown/all")
async def shutdown_vms_all( session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    status = shutdown_all_vms(session)

    if status is None:
        raise HTTPException(status_code=500, detail="Error al deteneter las mvs.")
    return status

@router.get("/{user_id}")
async def get_vms_user(user_id: str, session = Depends(get_session), current_user: UserBase = Depends(get_current_user)):
    vm = get_vms_user_service(user_id, session)

    if vm is None:
        raise HTTPException(status_code=500, detail="Error al obtener las MVs del usuario.")
    return vm

