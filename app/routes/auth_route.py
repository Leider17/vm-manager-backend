from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlmodel import Session, select
from app.core.db import get_session
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.models.user_model import User
from app.services.auth_service import register_user_service, login_for_access_token_service

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
    """
    Registra un nuevo usuario

    Args:
        como parametros recibe los datos del nuevo usuario y la session de la base de datos.

    Returns:
        el token de acceso, en caso de fallar devuelve un status 409 o 500.
    """
    result = register_user_service(user_create, session)
    if result is None:
        existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="email already registered"
            )
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error registering user"
            )
    return result

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Obtiene el token de acceso

    Args:
        como parametros recibe los datos del usuario y la session de la base de datos.

    Returns:
        el token de acceso, en caso de fallar devuelve un status 401.
    """
    result = login_for_access_token_service(
        UserLogin(email=form_data.username, password=form_data.password), 
        session
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentials are incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result