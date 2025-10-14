from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import create_all_tables
from app.routes.mv_route import router 
from app.routes.novnc_route import router as novnc_router
from app.routes.auth_route import router as auth_router
from app.routes.type_route import router as type_router
from app.services.novnc_service import validate_session
from app.core.websocket_proxy import stablish_tunnel


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

@app.websocket("/vnc-proxy/{token}")
async def vnc_websocket_handler(websocket: WebSocket, token: str):
    print(token)
    await websocket.accept()

    session = validate_session(token)
    if not session:
        await websocket.close(1000)
        return
    
    await stablish_tunnel(websocket, session)

app.include_router(router)
app.include_router(novnc_router)
app.include_router(auth_router)
app.include_router(type_router)

