from fastapi import HTTPException, Request, Response
import httpx
from app.core.guacamole_utils import get_auth_token, create_guacamole_connection

GUAC_TUNNEL_URL = "http://localhost:8080/guacamole/tunnel"

def create_guac_connection(vm_name: str, guac_host: str, vnc_port: str):
    try:
        token, datasource = get_auth_token()
        conn_id = create_guacamole_connection(token, datasource, vm_name, guac_host, vnc_port)

        return {
            "guac_token": token,
            "guac_datasource": datasource,
            "guac_id": str(conn_id),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando conexión Guacamole: {str(e)}")


def proxy_guac_request(method: str, path: str, headers: dict, params: dict, body: bytes = None) -> Response:
    try:
        url = f"{GUAC_TUNNEL_URL}{path}"  # respeta el /<uuid> también
        with httpx.Client() as client:
            guac_response = client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                content=body
            )
        return Response(
            content=guac_response.content,
            status_code=guac_response.status_code,
            headers=dict(guac_response.headers),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en proxy /tunnel: {str(e)}")



