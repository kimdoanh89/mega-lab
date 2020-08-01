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
            links_data = get_links_task.result().json()
            return nodes_data, links_data

    @classmethod
    def add_router(cls, id, x0, y0) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        node_url = project_url + f'/templates/{TEMPLATE_ID}'
        x, y = calculate_coordinates(id, x0, y0)
        response = httpx.post(node_url, json={"x": x, "y": y})
        return response
    
    @classmethod
    def add_link(cls, i, node_id1, node_id2) -> "GNS3Project":
        project_url = GNS3_CONTROLLER_API_ROOT + f'/projects/{PROJECT_ID}'
        link_url = project_url + f'/links'
        data = {"nodes": [{"node_id": node_id1, "adapter_number": 0, "port_number": i+1}, 
                          {"node_id": node_id2, "adapter_number": 0, "port_number": 1}],
                "filters": {}}
        httpx.post(link_url, json=data)
