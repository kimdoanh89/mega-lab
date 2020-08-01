import asyncio
import aiofiles
from jinja2 import Environment, FileSystemLoader
from app.contants import PROJECT_ID
from app.gns3_project import GNS3Project
from app.device import Device

MAX_NUMBER_ROUTER = 1000


async def generate_dhcp_config():
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template('dhcp2.j2')
    msg = template.render()
    async with aiofiles.open("output/dhcpd2.conf", "w") as f:
        f.write(msg)


async def main():
    # devices = [Device.from_sequence_num(i) for i in range(1, MAX_NUMBER_ROUTER + 1)]
    # await generate_dhcp_config()
    nodes_data = await GNS3Project.fetch_from_id(PROJECT_ID)
    # group = ["Switch1", "Switch2", "Switch3", "Switch4"]
    group = ["Switch1", "Switch2"]
    for k in range(len(group)):
        for i, node in enumerate(nodes_data):
            if node["name"] == group[k]:
                print("{} coordinates: {} {}".format(group[k], node["x"], node["y"]))
                x3, y3,  node_id_sw3 = node["x"], node["y"], node["node_id"]
                for i in range(0, 50):
                    node_id_router = GNS3Project.add_router(k, i, x3, y3)
                    GNS3Project.add_link(i, node_id_sw3, node_id_router)
    breakpoint()
    # TODO: Add asyncio context manager


if __name__ == "__main__":
    asyncio.run(main())
