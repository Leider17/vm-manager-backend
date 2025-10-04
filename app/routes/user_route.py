from fastapi import HTTPException,APIRouter, Body
from app.services.user_service import provision_vm
from app.schemas.user_schema import UserId
from app.services.user_service import start_vm_service, stop_vm_service, destroy_vm_service

router= APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/provision")
async def post_provision(UserId: UserId):
    vm=provision_vm(UserId)
    if vm is None:
        raise HTTPException(status_code=500, detail="Error en el aprovisionamiento de la MV.")
    return vm

@router.post("/start")
async def post_start(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    return start_vm_service(vm_name)

@router.post("/stop")
async def post_stop(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    return stop_vm_service(vm_name)

@router.post("/destroy")
async def post_destroy(payload: dict = Body(...)):
    vm_name = payload.get("vm_name")
    return destroy_vm_service(vm_name)