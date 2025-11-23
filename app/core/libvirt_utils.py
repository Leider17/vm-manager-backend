import libvirt
import subprocess
import xml.etree.ElementTree as ET
import time
import os
import uuid

def connect_to_libvirt():
    conn = libvirt.open('qemu:///system')
    info = conn.getInfo()
    if conn is None:
        raise Exception('Failed to open connection to qemu:///system')
    return conn


def clone_vm(source_name: str, new_name: str):
    conn = connect_to_libvirt()
    try:
        source_vm = conn.lookupByName(source_name)
        source_xml = source_vm.XMLDesc(0)
        
        root = ET.fromstring(source_xml)
        
        name_elem = root.find('name')
        name_elem.text = new_name
        
        uuid_elem = root.find('uuid')
        if uuid_elem is not None:
            root.remove(uuid_elem)
        
        disk = root.find(".//disk[@type='file']/source")
        if disk is not None:
            old_path = disk.get('file')
            new_path = old_path.rsplit('/', 1)[0] + '/' + new_name + '.qcow2'
            
            subprocess.run([
                'qemu-img', 'create', '-f', 'qcow2',
                '-b', old_path, '-F', 'qcow2', new_path
            ], check=True, capture_output=True)
            
            disk.set('file', new_path)
        
        for interface in root.findall(".//interface/mac"):
            interface.getparent().remove(interface)
        
        new_xml = ET.tostring(root, encoding='unicode')
        new_vm = conn.defineXML(new_xml)
        
        return new_vm
        
    except Exception as e:
        raise Exception(f"Failed to clone VM: {str(e)}")
    finally:
        conn.close()


def get_vm_vnc_port(vm_name: str):
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