from fastapi import FastAPI, HTTPException
import uuid
import threading
import time
from app.core.libvirt_utils import clone_vm, get_vm_vnc_port, destroy_vm
from app.core.guacamole_utils import get_auth_token, create_guacamole_connection

def provision_vm(student_id: str):
    vm_template_name = "MiVM"  

    vm_name = f"vm-{student_id}-{uuid.uuid4().hex[:6]}"
    try:
        clone_vm(vm_template_name, vm_name)
        
        time.sleep(20) 
        vnc_port = get_vm_vnc_port(vm_name)
        if not vnc_port:
            raise Exception("No se pudo obtener el puerto VNC de la MV.")
        
        return {
            "vm_name": vm_name,
            "vnc_port": vnc_port
        }

    except Exception as e:
        threading.Thread(target=lambda: destroy_vm(vm_name)).start()
        raise HTTPException(status_code=500, detail=f"Error en el aprovisionamiento: {str(e)}")