from app.core.connection_manager import ConnectionManager, manager
import libvirt
import asyncio
import threading
from datetime import datetime
from app.services.mv_service import sync_state_service
from sqlmodel import Session
from app.core.db import get_session
from fastapi import Depends

class LibvirtMonitor:
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.conn = None
        self.running = False
        self.monitor_task = None
        self.loop = None 
    
    def lifecycle_callback(self, conn, dom, event, detail, opaque):
        
        event_map = {
            libvirt.VIR_DOMAIN_EVENT_STARTED: "running",
            libvirt.VIR_DOMAIN_EVENT_STOPPED: "stopped",
            libvirt.VIR_DOMAIN_EVENT_SHUTDOWN: "shutdown",
            libvirt.VIR_DOMAIN_EVENT_SUSPENDED: "suspended",
            libvirt.VIR_DOMAIN_EVENT_RESUMED: "resumed",
        }
        
        try:
            session = next(get_session())
            vm_name = dom.name()
        except libvirt.libvirtError:
            vm_name = "unknown_vm" 
        event_type = event_map.get(event, f"unknown_detail_{detail}")
        sync_state_service(vm_name, session)
        
        message = {
            "type": "vm_event",
            "vm_name": vm_name,
            "event": event_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                self.manager.broadcast(message),
                self.loop
            )
        else:
            print(f" El bucle de eventos está cerrado. No se puede transmitir el evento para {vm_name}.")

    async def start_monitoring(self):
        """Inicia el monitoreo en un hilo separado"""
        if self.running:
            return
        
        self.running = True
        
        self.loop = asyncio.get_running_loop()
        libvirt.virEventRegisterDefaultImpl()
        
        def monitor_thread():
            try:
                self.conn = libvirt.open('qemu:///system')
                if not self.conn:
                    return
                
                self.conn.domainEventRegisterAny(
                    None,
                    libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                    self.lifecycle_callback,
                    None
                )
                
                while self.running:
                    libvirt.virEventRunDefaultImpl()
                    threading.Event().wait(0.1) 

            except Exception as e:
                import traceback
                traceback.print_exc()
            finally:
                if self.conn:
                    self.conn.close()
        
        thread = threading.Thread(target=monitor_thread, daemon=True)
        thread.start()
    
    async def stop_monitoring(self):
        self.running = False
        
monitor = LibvirtMonitor(manager)
