from typing import Annotated
from fastapi import Depends,FastAPI
from sqlmodel import SQLModel, create_engine, Session
from decouple import config 
from app.models.user_model import User
from app.models.vm_model import Vm


URL_DB=config("DATABASE_URL")
if not URL_DB:
    raise ValueError("DATABASE_URL is not set in the environment variables.")
engine = create_engine(URL_DB)

def create_all_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("All tables created successfully.")
    yield
    print("All tables creation process completed.")



def get_session():
    with Session(engine) as session:
        yield session


SessionLocal= Annotated[Session, Depends(get_session)] 