from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.db import create_all_tables
from app.routes.user_route import router 
from app.routes.guacamole_route import router as guac_router
from app.routes.novnc_route import router as novnc_router


app = FastAPI(lifespan=create_all_tables)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
async def root():
    return {"message": "Server is running"}

app.include_router(router)
app.include_router(guac_router)
app.include_router(novnc_router)