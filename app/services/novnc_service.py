import subprocess
import os
from fastapi import HTTPException

# Ruta donde están los archivos HTML de noVNC
NOVNC_PATH = "/usr/share/novnc"

# Mantener procesos levantados para no duplicar
active_tunnels = {}

def start_novnc(vm_name: str, vnc_port: int, ws_port: int = 6080):
    """
    Levanta un túnel websockify que expone el VNC en un puerto WS.
    """
    if vm_name in active_tunnels:
        return f"http://localhost:{ws_port}/vnc.html?host=localhost&port={ws_port}"

    try:
        cmd = [
            "websockify",
            "--web", NOVNC_PATH,
            str(ws_port),
            f"localhost:{vnc_port}"
        ]
        # Levanta el proceso en background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        active_tunnels[vm_name] = process

        return f"http://localhost:{ws_port}/vnc.html?host=localhost&port={ws_port}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando noVNC: {str(e)}")


def stop_novnc(vm_name: str):
    """
    Detiene el túnel websockify de una VM.
    """
    process = active_tunnels.get(vm_name)
    if process:
        process.terminate()
        process.wait()
        del active_tunnels[vm_name]
