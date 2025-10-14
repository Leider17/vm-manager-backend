from sqlmodel import Session, select
from datetime import timedelta
from typing import Union 
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.core.auth import get_password_hash, verify_password, create_access_token


def register_user_service(user_create: UserCreate, session: Session) -> Union[Token, None]:
    """
    Registra un nuevo usuario
    Args:
        session: la session de la base de datos.
        user_create: los datos del nuevo usuario.

    Returns:
        el token de acceso
    """
    try:
        existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_user:
            return None 

        hashed_password = get_password_hash(user_create.password)
        db_user = User(name=user_create.name, email=user_create.email, password=hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        access_token_expires = timedelta(minutes=60)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Error en register_user_service: {e}")
        return None 

def login_for_access_token_service(user_login: UserLogin, session: Session) -> Union[Token, None]:
    """
    Obtiene el token de acceso
    Args:
        session: La sesión de la base de datos.
        user_login: Los datos del usuario.

    Returns:
        el token de acceso
    """
    try:
        user = session.exec(select(User).where(User.email == user_login.email)).first()
        if not user or not verify_password(user_login.password, user.password):
            return None 

        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except Exception as e:
        print(f"Error in login_for_access_token_service: {e}")
        return None 