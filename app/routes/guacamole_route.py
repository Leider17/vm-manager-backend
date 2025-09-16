from fastapi import HTTPException,APIRouter, Request
from app.services.guacamole_service import create_guac_connection, proxy_guac_request


router= APIRouter(
    prefix="/tunnel",
    tags=["guacamole"]
)

@router.post("/connect")
async def post_connect(data: dict):
    vm_name = data.get("vm_name")
    guac_host = data.get("guac_host")
    vnc_port = data.get("vnc_port")

    if not all([vm_name, guac_host, vnc_port]):
        raise HTTPException(status_code=400, detail="Faltan parámetros requeridos.")

    guac_data = create_guac_connection(vm_name, guac_host, vnc_port)
    return guac_data


@router.api_route("/{full_path:path}", methods=["GET", "POST"])
async def any_tunnel(full_path: str, request: Request):
    body = await request.body()
    params = dict(request.query_params)
    headers = dict(request.headers)

    return  proxy_guac_request(
        method=request.method,
        path="/" + full_path,  # incluye /<uuid> si existe
        headers=headers,
        params=params,
        body=body
    )
