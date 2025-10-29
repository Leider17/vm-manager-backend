from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from app.core.connection_manager import manager

from app.core.db import get_session
from app.core.db import create_all_tables
from app.routes.mv_route import router 
from app.routes.novnc_route import router as novnc_router
from app.routes.auth_route import router as auth_router
from app.routes.type_route import router as type_router
from app.services.novnc_service import validate_session
from app.services.mv_service import sync_state_service, get_all_vms_service
from app.core.websocket_proxy import stablish_tunnel
from app.libvirt_monitor import monitor
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):    
    try:
        if asyncio.iscoroutinefunction(create_all_tables):
            await create_all_tables(app)
        else:
            create_all_tables(app)
    except Exception as e:
        print(f"Error al inicializar la DB con create_all_tables(app): {e}")


    await monitor.start_monitoring()
    
    yield
    await monitor.stop_monitoring()




app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods=["*"],
    allow_headers=["*"],
)



# app = FastAPI(lifespan=create_all_tables)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins="*",
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



@app.get("/")
async def root():
    return {"message": "Server is running"}

@app.websocket("/vnc-proxy/{token}")
async def vnc_websocket_handler(websocket: WebSocket, token: str):
    await websocket.accept()

    session = validate_session(token)
    if not session:
        await websocket.close(1000)
        return
    
    await stablish_tunnel(websocket, session)

# @app.websocket("/stateVm")
# async def validate_state(websocket: WebSocket, session: Session = Depends(get_session)):
#     await websocket.accept()
#     prev_state = {}
#     while True:
#         for vm in get_all_vms_service(session):
#             currentVm = sync_state_service(vm.name, session)
#             print(currentVm)
#             if (currentVm.state != prev_state.get(vm.name)):
#                 print(currentVm)
#                 await websocket.send_json(currentVm.model_dump())
#                 prev_state[vm.name] = currentVm.state
#         await asyncio.sleep(5)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado al monitor de VMs",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

app.include_router(router)
app.include_router(novnc_router)
app.include_router(auth_router)
app.include_router(type_router)

