import libvirt
import subprocess
import uuid
import re
import xml.etree.ElementTree as ET

def connect_to_libvirt():
    conn = libvirt.open('qemu:///system')
    if conn is None:
        raise Exception('Failed to open connection to qemu:///system')
    return conn


def clone_vm(source_name: str, new_name: str):
    """Clona una VM usando virt-clone (requiere libvirt-client)"""
    try:
        cmd = [
            'virt-clone',
            '--original', source_name,
            '--name', new_name,
            '--auto-clone'
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        conn = connect_to_libvirt()
        try:
            vm = conn.lookupByName(new_name)
            vm.create()
            return vm
        finally:
            conn.close()
            
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone VM: {e.stderr}")


def get_vm_vnc_port(vm_name: str):
    """Obtiene el puerto VNC de una MV por su nombre."""
    print("Obteniendo puerto VNC de la MV:", vm_name)
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(vm_name)
        xml_desc = vm.XMLDesc(0)
        root = ET.fromstring(xml_desc)
        graphics = root.find(".//graphics[@type='vnc']")
        print(vm_name, "puerto VNC probando")
        if graphics is not None:
            print(vm_name, "puerto VNC:", graphics.get("port"))
            return graphics.get("port")
        return None
    finally:
        conn.close()

def start_vm(name: str):
    conn = connect_to_libvirt()
    vm = conn.lookupByName(name)
    if vm is None:
        raise Exception(f'VM {name} not found')
    vm.create()

def stop_vm(name: str):
    conn = connect_to_libvirt()
    vm = conn.lookupByName(name)
    if vm is None:
        raise Exception(f'VM {name} not found')
    vm.shutdown()

def destroy_vm(name: str): 
    conn = connect_to_libvirt()
    vm = conn.lookupByName(name)
    if vm is None:
        raise Exception(f'VM {name} not found')
    vm.destroy()
    vm.undefine()