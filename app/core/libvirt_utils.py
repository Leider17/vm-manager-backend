import libvirt
import subprocess
import xml.etree.ElementTree as ET
import time
import os

def connect_to_libvirt():
    conn = libvirt.open('qemu:///system')
    info = conn.getInfo()
    if conn is None:
        raise Exception('Failed to open connection to qemu:///system')
    return conn


def clone_vm(source_name: str, new_name: str):
    """Clona una VM usando virt-clone (requiere libvirt-client)"""
    try:
        cmd = [
            '/usr/bin/virt-clone',
            '--original', source_name,
            '--name', new_name,
            '--auto-clone'
        ]
        subprocess.run(cmd, check = True, capture_output = True, text = True)
        conn = connect_to_libvirt()
        try:
            vm = conn.lookupByName(new_name)
            # vm.create()
            return vm
        finally:
            conn.close()    
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone VM: {e.stderr}")


def get_vm_vnc_port(vm_name: str):
    """Obtiene el puerto VNC de una MV por su nombre."""
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(vm_name)
        xml_desc = vm.XMLDesc(0)
        root = ET.fromstring(xml_desc)
        graphics = root.find(".//graphics[@type='vnc']")
        if graphics is not None:
            return graphics.get("port")
        return None
    finally:
        conn.close()

def start_vm(name: str):
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(name)
    except libvirt.libvirtError:
        raise Exception(f'VM {name} not found')
    vm.create()

def stop_vm(name: str):
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(name)
    except libvirt.libvirtError:
        raise Exception(f'VM {name} not found')
    vm.destroy()

def destroy_vm(name: str): 
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(name)
    except libvirt.libvirtError:
        raise Exception(f'VM {name} not found')
    try:
        if vm.isActive():
            vm.destroy()
        subprocess.run(["virsh", "undefine", "--remove-all-storage", name])
        # xml_desc = vm.XMLDesc(0)
        # root = ET.fromstring(xml_desc)
        # disk_path = root.find(".//disk/source").get("file")
        # vm.undefine()
        # os.remove(disk_path)
    except libvirt.libvirtError as e:
        raise Exception(f'Failed to destroy VM {name}: {e}')
    
def get_info_vm (name: str):
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(name)
    except libvirt.libvirtError:
        raise Exception(f'VM {name} not found')
    state, max_mem, mem, num_cpu, cpu_time = vm.info()
    xml_desc = vm.XMLDesc(0)
    root = ET.fromstring(xml_desc)
    disk_path = root.find(".//disk/source").get("file")
    disk_size = vm.blockInfo(disk_path)[0]
    actual_usage = vm.blockInfo(disk_path)[1]
    
    state_dict = {
        libvirt.VIR_DOMAIN_NOSTATE: 'no state',
        libvirt.VIR_DOMAIN_RUNNING: 'running',
        libvirt.VIR_DOMAIN_BLOCKED: 'blocked',
        libvirt.VIR_DOMAIN_PAUSED: 'paused',
        libvirt.VIR_DOMAIN_SHUTDOWN: 'shutdown',
        libvirt.VIR_DOMAIN_SHUTOFF: 'shut off',
        libvirt.VIR_DOMAIN_CRASHED: 'crashed',
        libvirt.VIR_DOMAIN_PMSUSPENDED: 'suspended by guest power management'
    }

    return {
        'state': state_dict.get(state, 'unknown'),
        'max_mem': max_mem / 1048576,
        'mem': mem / 1048576,
        'num_cpu': num_cpu,
        'cpu_time': cpu_time,
        'disk_size': disk_size / 1048576,
        'disk_usage': actual_usage / 1048576
    }

def get_state_vm(name:str):
    conn = connect_to_libvirt()
    try:
        vm = conn.lookupByName(name)
    except libvirt.libvirtError:
        raise Exception(f'VM {name} not found')
    if vm.isActive():
        return "running"
    else:
        return "stopped"
    
