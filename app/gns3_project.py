import httpx
import asyncio

from app.contants import GNS3_CONTROLLER_API_ROOT, PROJECT_ID, TEMPLATE_ID
from app.utils import calculate_coordinates


class GNS3Project:
    def __init__(self, id: str) -> None:
        self.id = id
        self.http_client = httpx.AsyncClient()

    async def __aenter__(self) -> None:
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.http_client.aclose()

    @classmethod
    async def fetch_from_id(cls, id: str) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        async with httpx.AsyncClient() as http_client:
            get_nodes_task = asyncio.create_task(
                http_client.get(f'{project_url}/nodes'))
            get_links_task = asyncio.create_task(
                http_client.get(f'{project_url}/links'))
            await asyncio.gather(get_nodes_task, get_links_task)
            nodes_data = get_nodes_task.result().json()
            # links_data = get_links_task.result().json()
            return nodes_data

    @classmethod
    def add_router(cls, k, id, x0, y0) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        node_url = project_url + f'/templates/{TEMPLATE_ID}'
        x, y = calculate_coordinates(id, x0, y0)
        response = httpx.post(node_url, json={"x": x, "y": y})
        res = response.json()
        node_id_router = res['node_id']
        if response.status_code == 201:
            print("R{} is successfully created!".format(k*50+id+1))
        start_url = project_url + f'/nodes/{node_id_router}/start'
        resp2 = httpx.post(start_url, data={})
        if resp2.status_code == 200:
            print("R{} is successfully started!".format(k*50+id+1))
        else:
            print(resp2.text)
        return node_id_router
    
    @classmethod
    def add_link(cls, i, node_id1, node_id2) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        link_url = project_url + f'/links'
        data = {"nodes": [{"node_id": node_id1, "adapter_number": 0, "port_number": i+1}, 
                          {"node_id": node_id2, "adapter_number": 0, "port_number": 0}],
                "filters": {}}
        resp = httpx.post(link_url, json=data)
        if resp.status_code == 201:
            print("Link btw Switch and router is added!!")
        return resp
    
    @classmethod
    def delete_router(cls, node_id) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        node_url = project_url + f'/nodes/{node_id}'
        httpx.delete(node_url)
