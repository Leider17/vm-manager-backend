import secrets
import json
import redis
from fastapi import HTTPException
from app.core.libvirt_utils import get_vm_vnc_port

redis_client = redis.Redis (host = "localhost", port = 6379, decode_responses = False)

def create_session(user_id: str, vm_name: str):
    vnc_port = get_vm_vnc_port(vm_name)
    
    if (vnc_port):
        token = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "vm_name": vm_name,
            "vnc_port": vnc_port,
        }

        redis_client.setex(f"vncToken:{token}", 900, json.dumps(session_data))
        return token
    else:
        raise HTTPException(503, "VNC server not available")
        
    
def validate_session(token: str):
    session = redis_client.get(f"vncToken:{token}")
    if not session:
        return None

    # redis_client.delete(f"vncToken:{token}")
    return json.loads(session)



