from fastapi import FastAPI, HTTPException
import uuid
import threading
import time
from sqlmodel import Session, select
from app.models.vm_model import Vm
from app.core.libvirt_utils import clone_vm, destroy_vm, start_vm, stop_vm, get_info_vm, get_vm_vnc_port

def provision_vm(student_id: str, vm_type: str, session: Session):
    vm_template_name = "MiVM"  

    vm_name = f"vm-{student_id}-{uuid.uuid4().hex[:6]}"
    try:
        clone_vm(vm_template_name, vm_name)

        # time.sleep(20) 
        vnc_port = get_vm_vnc_port(vm_name)
        vm = Vm(name = vm_name, vnc_port = vnc_port, state = "running", user_id = student_id, type_id = vm_type )
        session.add(vm)
        session.commit()
        session.refresh(vm)
        return { 
            "vm_name": vm_name, 
            "status": "success", 
            "vm": vm 
        }

    except Exception as e:
        threading.Thread(target = lambda: destroy_vm(vm_name)).start()
        raise HTTPException(status_code = 500, detail = f"Error en el aprovisionamiento: {str(e)}")
    
def start_vm_service(vm_name: str, session: Session):
    try:
        start_vm(vm_name)
        vm = update_vm_status_service(vm_name, "running", session)
        return {
            "vm": vm,
            "status": "success",
            "message": f"MV {vm_name} iniciada correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al iniciar la MV: {str(e)}")

def stop_vm_service(vm_name: str, session: Session):
    try:
        stop_vm(vm_name)
        vm = update_vm_status_service(vm_name, "stopped", session)
        return {
            "vm": vm,
            "status": "success",
            "message": f"MV {vm_name} detenida correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al detener la MV: {str(e)}")

def destroy_vm_service(vm_name: str, vm_id: int, session: Session):
    try:
        destroy_vm(vm_name)
        vm = session.get(Vm, vm_id)
        print(vm)
        if not vm:
            raise HTTPException(status_code = 404, detail = 'vm no encontrada')
        session.delete(vm)
        session.commit
        return {
            "status": "success",
            "message": f"MV {vm_name} destruida correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al destruir la MV: {str(e)}")

def get_vms_user_service(user_id: str, session: Session):
    try:
        vms= session.exec(select(Vm).where(Vm.user_id == user_id)).all()
        return vms
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener las Vms del usuario: {str(e)}")
    
def get_all_vms_service(session: Session):
    try:
        vms= session.exec(select(Vm)).all()
        return vms
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener las Vms: {str(e)}")
    
def get_info_vm_service(vm_name: str):
    try:
        info = get_info_vm(vm_name)
        return info
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener la información de la Vm: {str(e)}")
    
def validate_vm_ownership(vm_name: str, user_id: str, session: Session):
    try:
        vm = session.exec(select(Vm).where(Vm.name == vm_name, Vm.user_id == user_id)).first()
        if not vm:
            raise HTTPException(status_code = 404, detail = "Vm no encontrada o no pertenece al usuario.")
        return vm
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al validar la propiedad de la Vm: {str(e)}")
    
def update_vm_status_service(vm_name: str, state: str, session: Session):
    try:
        vm = session.exec(select(Vm).where(Vm.name == vm_name)).first()
        if not vm:
            raise HTTPException(status_code = 404, detail = "MV no encontrada.")
        vm.state = state
        session.add(vm)
        session.commit()
        session.refresh(vm)
        return vm
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al actualizar el estado de la MV: {str(e)}")