import asyncio
from fastapi import WebSocket

async def stablish_tunnel(websocket: WebSocket, session_data):
    vnc_host = "localhost" 
    vnc_port = session_data["vnc_port"]
    vnc_writer = None 

    try:
        vnc_reader, vnc_writer = await asyncio.open_connection(vnc_host, int(vnc_port))
        server_version = await vnc_reader.read(12)
        if not server_version:
            await websocket.close(1000, "VNC server closed during handshake")
            return
        await websocket.send_bytes(server_version)
        client_version_msg = await websocket.receive_bytes()
        client_version = client_version_msg 
        vnc_writer.write(client_version)
        await vnc_writer.drain()
        await proxy_bidirectional(websocket, vnc_reader, vnc_writer)

    except ConnectionRefusedError:
        await websocket.close(1000, f"Connection refused to VNC host {vnc_host}:{vnc_port}")
    except Exception as e:
        await websocket.close(1011, "Internal server error during VNC proxy")
    finally:
        if vnc_writer:
            vnc_writer.close()
            await vnc_writer.wait_closed()


async def proxy_bidirectional(websocket: WebSocket, vnc_reader: asyncio.StreamReader, vnc_writer: asyncio.StreamWriter):
    async def ws_to_vnc():
        try:
            async for message in websocket.iter_bytes():
                vnc_writer.write(message)
                await vnc_writer.drain()
        except Exception as e:
            print("Error en ws_to_vnc (cliente noVNC):", e)
        finally:
            vnc_writer.close()
    
    async def vnc_to_ws():
        print("Iniciando vnc_to_ws")
        while not vnc_reader.at_eof():
            try:
                data = await vnc_reader.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
            except Exception as e:
                break

    await asyncio.gather(ws_to_vnc(), vnc_to_ws(), return_exceptions=True)