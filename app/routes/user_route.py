from fastapi import HTTPException,APIRouter
from app.services.user_service import provision_vm
from app.schemas.user_schema import UserId

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