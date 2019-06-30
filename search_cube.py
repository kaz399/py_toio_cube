import sys
import asyncio
from bleak import discover
from bleak import BleakClient

TOIO_SERVICE_UUID = "10B20100-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BATTERY_UUID = "10B20108-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BUTTON_UUID = "10B20107-5B3B-4571-9508-CF3EFCD7BBAE".lower()

cubes = []

async def search_cube(loop):
    devices = await discover()
    for d in devices:
        try:
            async with BleakClient(d.address, loop=loop) as client:
                services = await client.get_services()
                cube = services.services.get(TOIO_SERVICE_UUID)
                if cube is not None:
                    cubes.append(cube)
                    print('toio core cube(%d): ' % len(cubes))
                    print('  Address: ', d.address)
                    for service in services:
                        print('  Service: ', service)
                        print('  UUID   : ', service.uuid)
        except:
            pass

def main(argv):
    print('search toio core cube')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_cube(loop))
    if len(cubes) == 0:
        print('sorry, no cubes are found')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
