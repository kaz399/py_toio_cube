#!/usr/bin/env python3

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import asyncio
from bleak import discover
from bleak import BleakClient

TOIO_SERVICE_UUID = "10B20100-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BATTERY_UUID = "10B20108-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BUTTON_UUID = "10B20107-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_SOUND_UUID = "10B20104-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_MOTOR_UUID = "10B20102-5B3B-4571-9508-CF3EFCD7BBAE".lower()

cubes = []

async def sound(cube):
    sound = bytearray()
    sound.append(0x02)
    sound.append(9)
    sound.append(0xff)
    await cube.write_gatt_char(TOIO_SOUND_UUID, sound)

async def motor(cube):
    motor = bytearray()
    motor.append(0x02)
    motor.append(0x01)
    motor.append(0x01)
    motor.append(0x10)
    motor.append(0x02)
    motor.append(0x01)
    motor.append(0x10)
    motor.append(0x40)
    await cube.write_gatt_char(TOIO_MOTOR_UUID, motor)

async def search_cube(loop):
    devices = await discover(timeout=2.0)
    for d in devices:
        try:
            async with BleakClient(d.address, loop=loop) as client:
                services = await client.get_services()
                connected = await client.is_connected()
                cube = services.services.get(TOIO_SERVICE_UUID)
                if cube is not None:
                    cubes.append(client)
                    print('toio core cube(%d): %s' % (len(cubes), connected))
                    print('  Address: ', d.address)
                    for service in services:
                        print('  Service: ', service)
                        print('  UUID   : ', service.uuid)
                        for char in service.characteristics:
                            print('    Characteristic: ', char)
                    await sound(client)
                    await motor(client)
        except Exception as e:
            print(e)
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
