import requests

GUAC_URL = "http://localhost:8080/guacamole/api"
GUAC_USER = "guacadmin"
GUAC_PASS = "guacadmin"


def get_auth_token():
    data = {"username": GUAC_USER, "password": GUAC_PASS}
    response = requests.post(f"{GUAC_URL}/tokens", data=data)
    response.raise_for_status()
    result = response.json()
    return result["authToken"], result["dataSource"]


def create_guacamole_connection(token: str, datasource: str, vm_name: str, host: str, port: str):
    """Crea una conexión en Guacamole para una VM."""
    headers = {"Content-Type": "application/json"}
    params = {"token": token}
    data = {
        "name": vm_name,
        "protocol": "vnc",
        "parentIdentifier": "ROOT",
        "attributes": {},
        "parameters": {
            "hostname": host,
            "port": str(port)
        }
    }
    response = requests.post(
        f"{GUAC_URL}/session/data/{datasource}/connections", 
        params=params,
        json=data
    )
    response.raise_for_status()
    return response.json()["identifier"]


# def get_connection_token(auth_token:str, connection_id: str):
#     params = {"token": auth_token}
#     response = requests.get(f"{GUAC_URL}/connections/{connection_id}/token", params=params)
#     response.raise_for_status()
#     return response.json()[connection_id]["token"]
