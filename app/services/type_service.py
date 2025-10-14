from sqlmodel import Session, select
from app.models.type_model import Type
from fastapi import HTTPException

def get_all_types_service (session: Session):
    try:
        types = session.exec(select(Type)).all()
        return types
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Error al obtener los tipos: {str(e)}")

