from fastapi import FastAPI, HTTPException
import uuid
import threading
import time
import psutil
from sqlmodel import Session, select
from app.models.vm_model import Vm, VmRead, VmComplete
from app.models.type_model import Type
from app.models.type_model import Type
from app.models.user_model import User
from app.core.libvirt_utils import clone_vm, destroy_vm, start_vm, stop_vm, get_info_vm, get_vm_vnc_port, get_state_vm
from app.core.log_utils import log_performance

def provision_vm(student_id: str, type_id: str, session: Session):
    type_vm = session.exec(select(Type).where(Type.id == type_id)).first()
    vm_name = f"vm-{uuid.uuid4().hex[:6]}"
    host_resources = get_info_host_service()
    
    resources = validate_resources(type_vm.name,'creation')
    if not resources['can_proceed']:
        raise HTTPException(status_code=409, detail="Recursos insuficientes para crear la máquina")
    try:
        start_time = time.time()
        clone_vm(type_vm.name, vm_name)
        vnc_port = get_vm_vnc_port(vm_name)
        vm = Vm(name = vm_name, vnc_port = vnc_port, state = "stopped", user_id = student_id, type_id = type_id )
        session.add(vm)
        session.commit()
        session.refresh(vm)
        end_time = time.time()
        log_performance(operation="clone", vm_name=type_vm.name, duration = end_time - start_time, status='success', host_memory=host_resources['used_memory'], used_disk=host_resources['used_disk'], cpu_cores=host_resources['cpu-cores'])
        return VmRead(
                id = vm.id,
                name = vm.name,
                vnc_port = vm.vnc_port,
                state = vm.state,
                user_id = vm.user_id,
                type_id = vm.type_id,
                type_name = vm.vm_type.name 
            )

    except Exception as e:
        # threading.Thread(target = lambda: destroy_vm(vm_name)).start()
        raise HTTPException(status_code = 500, detail = f"Error en el aprovisionamiento: {str(e)}")
    
def start_vm_service(vm_name: str, session: Session):
    host_resources = get_info_host_service()
    resources = validate_resources(vm_name,'start')
    if not resources['can_proceed']:
        raise HTTPException(status_code=409, detail="Recursos insuficientes en el host para iniciar la máquina")
    try:
        start_time = time.time()
        start_vm(vm_name)
        vm = update_vm_status_service(vm_name, "running", session)
        end_time = time.time()
        log_performance(operation="start", vm_name=vm.vm_type.name, duration = end_time - start_time, status='success', host_memory=host_resources['used_memory'], used_disk=host_resources['used_disk'], cpu_cores=host_resources['cpu-cores'])
        return VmRead(
                    id = vm.id,
                    name = vm.name,
                    vnc_port = vm.vnc_port,
                    state = vm.state,
                    user_id = vm.user_id,
                    type_id = vm.type_id,
                    type_name = vm.vm_type.name 
                )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al iniciar la MV: {str(e)}")

def stop_vm_service(vm_name: str, session: Session):
    host_resources = get_info_host_service()
    try:
        start_time = time.time()
        stop_vm(vm_name)
    
        vm = update_vm_status_service(vm_name, "stopped", session)
        end_time = time.time()
        log_performance(operation="stop", vm_name=vm.vm_type.name, duration = end_time - start_time, status='success', host_memory=host_resources['used_memory'], used_disk=host_resources['used_disk'], cpu_cores=host_resources['cpu-cores'])
        return VmRead(
                    id = vm.id,
                    name = vm.name,
                    vnc_port = vm.vnc_port,
                    state = vm.state,
                    user_id = vm.user_id,
                    type_id = vm.type_id,
                    type_name = vm.vm_type.name 
                )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al detener la MV: {str(e)}")

def destroy_vm_service(vm_name: str, vm_id: int, session: Session):
    try:
        vm = session.get(Vm, vm_id)
        if not vm:
            raise HTTPException(status_code = 404, detail = 'vm no encontrada')
        destroy_vm(vm_name)
        session.delete(vm)
        session.commit()
        return {
            "status": "success",
            "message": f"MV {vm_name} destruida correctamente."
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al destruir la MV: {str(e)}")

def get_vms_user_service(user_id: str, session: Session):
    try:
        vms = session.exec(select(Vm).join(Type).where(Vm.type_id == Type.id).where(Vm.user_id == user_id)).all()
        result = [
            VmRead(
                id = vm.id,
                name = vm.name,
                vnc_port = vm.vnc_port,
                state = vm.state,
                user_id = vm.user_id,
                type_id = vm.type_id,
                type_name = vm.vm_type.name 
            )
            for vm in vms
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener las Vms del usuario: {str(e)}")
    
def get_all_vms_service(session: Session):
    try:
        vms = session.exec(select(Vm).join(User)).all()
        result = [
            VmComplete(
                id = vm.id,
                name = vm.name,
                vnc_port = vm.vnc_port,
                state = vm.state,
                user_id = vm.user_id,
                user_name = vm.user.name,
                type_id = vm.type_id,
                type_name = vm.vm_type.name 
            )
            
            for vm in vms
            ]
        return result
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener las Vms: {str(e)}")
    
def get_info_vm_service(vm_name: str):
    try:
        info = get_info_vm(vm_name)
        return info
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al obtener la información de la Vm: {str(e)}")
    
def get_info_host_service():
    try:
        virtual_memory = psutil.virtual_memory()
        cpu_info = psutil.cpu_count(logical = True)
        disk = psutil.disk_usage("/var/lib/libvirt/images")
        info = {
            "total_memory": (virtual_memory.total / 1048576),
            "used_memory" : (virtual_memory.used / 1048576),
            "available_memory": (virtual_memory.available / 1048576),
            "cpu_cores": cpu_info,
            "used_disk": disk.used / 1048576,
            "free_disk": disk.free / 1048576
        }
        return info
    except Exception as e: 
        raise HTTPException(status_code = 500, detail = f"Error al obtener la información del host: {str(e)}")
    
def validate_resources(vm_name: str, operation_type: str):
    try:
        host_resources = get_info_host_service()
        
        if operation_type == 'creation':
            if not vm_name:
                raise HTTPException(status_code=400, detail="vm_name requerido para creación")
            base_vm_resources = get_info_vm(vm_name)
            required_memory = base_vm_resources['max_mem']
            required_cpus = base_vm_resources['num_cpu']
            required_disk = base_vm_resources['disk_size']
            
        elif operation_type == 'start':
            vm_resources = get_info_vm(vm_name)
            required_memory = vm_resources['max_mem']
            required_cpus = vm_resources['num_cpu']
            required_disk = 0
            
        else:
            raise HTTPException(status_code=400, detail="operation_type debe ser 'creation' o 'start'")
        
        memory_buffer = 0.15
        cpu_oversubscription = 2.0
        disk_buffer = 0.20
        
        available_memory = host_resources['available_memory'] * (1 - memory_buffer)
        available_cpus = host_resources['cpu_cores'] * cpu_oversubscription
        available_disk = host_resources['free_disk'] * (1 - disk_buffer)
        
        validations = {
            'memory': {
                'valid': available_memory >= required_memory,
                'available_mb': round(available_memory, 2),
                'required_mb': round(required_memory, 2),
                'usage_percentage': round((required_memory / available_memory) * 100, 2) if available_memory > 0 else 0
            },
            'cpu': {
                'valid': available_cpus >= required_cpus,
                'available_cores': available_cpus,
                'required_cores': required_cpus,
                'usage_percentage': round((required_cpus / available_cpus) * 100, 2) if available_cpus > 0 else 0
            },
            'disk': {
                'valid': available_disk >= required_disk if operation_type == 'creation' else True,
                'available_mb': round(available_disk, 2),
                'required_mb': round(required_disk, 2),
                'usage_percentage': round((required_disk / available_disk) * 100, 2) if available_disk > 0 and operation_type == 'creation' else 0
            }
        }
        
        overall_valid = all(validation['valid'] for validation in validations.values())
        
        return {
            'can_proceed': overall_valid,
            'operation_type': operation_type,
            'target_vm': vm_name,
            'base_vm': vm_name if operation_type == 'creation' else None,
            'resource_analysis': validations,
            'host_info': {
                'total_memory_mb': round(host_resources['total_memory'], 2),
                'total_cpus': host_resources['cpu_cores'],
                'total_disk_mb': round(host_resources['free_disk'] + host_resources['used_disk'], 2)
            }
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error validando recursos: {str(e)}")

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
    
def sync_state_service(vm_name: str, session: Session):
    try:
        state = get_state_vm(vm_name)
        vm = session.exec(select(Vm).where(Vm.name == vm_name)).first()
        if (state == "running"):
            vm.state = "running"
        else:
            vm.state = "stopped"
        session.add(vm)
        session.commit()
        session.refresh(vm)
        return vm
    except Exception as e:
        print("error al sincronizar el estado de la máquina")
    
def shutdown_vms_user_service(user_id: str, session: Session):
    try:
        vms = session.exec(select(Vm).where((Vm.user_id == user_id) & (Vm.state == "running"))).all()

        for vm in vms:
            stop_vm(vm.name)
            update_vm_status_service(vm.name, "stopped", session)
        return {
            "status": "success",
            "message": f"Mvs detenidas correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al detener las máquinas {str(e)}" )
    
def shutdown_all_vms(session: Session):
    try:
        vms = session.exec(select(Vm).where(Vm.state == "running")).all()

        for vm in vms:
            stop_vm(vm.name)
            update_vm_status_service(vm.name, "stopped", session)
        return {
            "status": "success",
            "message": f"Mvs detenidas correctamente"
        }
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Error al detener las máquinas {str(e)}" )
