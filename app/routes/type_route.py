from fastapi import HTTPException,APIRouter
from app.core.db import get_session
from app.services.type_service import get_all_types_service
from fastapi import Depends
from app.core.db import get_session

router= APIRouter(
    prefix="/type",
    tags=["type"]
)

@router.get("/all")
async def get_all_types(session=Depends(get_session)):
    types = get_all_types_service(session)
    if types is None:
        raise HTTPException(status_code=500, detail="Error al obtener las MVs.")
    return types

