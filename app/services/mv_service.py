from fastapi import FastAPI, HTTPException
import uuid
import threading
import time
from sqlmodel import Session, select
from app.models.vm_model import Vm
from app.core.libvirt_utils import clone_vm, get_vm_vnc_port, destroy_vm, start_vm, stop_vm

def provision_vm(student_id: str):
    vm_template_name = "MiVM"  

    vm_name = f"vm-{student_id}-{uuid.uuid4().hex[:6]}"
    try:
        clone_vm(vm_template_name, vm_name)
        
        time.sleep(20) 

        return {
            "vm_name": vm_name,
            "status": "success",
        }

    except Exception as e:
        threading.Thread(target=lambda: destroy_vm(vm_name)).start()
        raise HTTPException(status_code=500, detail=f"Error en el aprovisionamiento: {str(e)}")
    
def start_vm_service(vm_name: str):
    try:
        start_vm(vm_name)
        return {
            "status": "success",
            "message": f"MV {vm_name} iniciada correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar la MV: {str(e)}")

def stop_vm_service(vm_name: str):
    try:
        stop_vm(vm_name)
        return {
            "status": "success",
            "message": f"MV {vm_name} detenida correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al detener la MV: {str(e)}")

def destroy_vm_service(vm_name: str):
    try:
        destroy_vm(vm_name)
        return {
            "status": "success",
            "message": f"MV {vm_name} destruida correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al destruir la MV: {str(e)}")

def get_vms_user_service(user_id: str, session: Session):
    try:
        vms= session.exec(select(MV).where(MV.user_id == user_id)).all()
        return vms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las MVs del usuario: {str(e)}")
    
def get_all_vms_service(session: Session):
    try:
        vms= session.exec(select(MV)).all()
        return vms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las MVs: {str(e)}")
    
def validate_vm_ownership(vm_name: str, user_id: str, session: Session):
    try:
        vm = session.exec(select(MV).where(MV.name == vm_name, MV.user_id == user_id)).first()
        if not vm:
            raise HTTPException(status_code=404, detail="MV no encontrada o no pertenece al usuario.")
        return vm
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar la propiedad de la MV: {str(e)}")