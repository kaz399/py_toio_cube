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
import time
from bleak import discover
from bleak import BleakClient
from bleak import exc

TOIO_SERVICE_UUID = "10B20100-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BATTERY_UUID = "10B20108-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_BUTTON_UUID = "10B20107-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_SOUND_UUID = "10B20104-5B3B-4571-9508-CF3EFCD7BBAE".lower()
TOIO_MOTOR_UUID = "10B20102-5B3B-4571-9508-CF3EFCD7BBAE".lower()


async def sound(cube, tone):
    sound = bytearray()
    sound.append(0x03)
    sound.append(0x01)
    sound.append(0x01)
    sound.append(40)
    sound.append(55 + tone)
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


async def move_action(cube_id, cube, tone):
    for ct in range(8):
        if ct < 3:
            tone = ct * 2
        elif ct < 7:
            tone = (ct * 2) - 1
        else:
            tone = (ct * 2) - 2

        tone += (cube_id * 3)

        await sound(cube, tone)
        await motor(cube)
        await asyncio.sleep(1)


async def move_pattern1(cube,tone):
    await sound(cube, tone)
    await motor(cube)
    await asyncio.sleep(1)


async def get_connection(device, loop):
    cube = BleakClient(device.address, loop)
    time.sleep(1)
    try:
        result = await cube.connect()
    except exc.BleakError as e:
        print(e)
    except AttributeError as e:
        pass

    connected = await cube.is_connected()
    if not connected:
        print('%s is not connected' % device.address)
        return None
    print('connect to:', device.address, cube, result)
    return cube


async def connect_and_move(device, loop):
    try:
        async with BleakClient(device.address, loop=loop) as cube:
            time.sleep(1)
            connected = await cube.is_connected()
            if not connected:
                print('%s is not connected' % device.address)
                return
            else:
                time.sleep(1)
            print('get service list')
            services = await cube.get_services()
            is_toio_cube = services.services.get(TOIO_SERVICE_UUID)
            if is_toio_cube is not None:
                cubes.append(cube)
                print('toio core cube(%d): %s' % (len(cubes), connected))
                print('  Address: ', device.address)
                for service in services:
                    print('  Service: ', service)
                    print('  UUID   : ', service.uuid)
                    for char in service.characteristics:
                        print('    Characteristic: ', char)
                for tone in range(10):
                    await move_pattern1(cube, tone)
    except exc.BleakError as e:
        print(e)
    except AttributeError as e:
        pass


async def search_and_move(loop):
    devices = await discover(timeout=2.0)
    cube_commands = []
    for btdev in devices:
        cube = await get_connection(btdev, loop)
        if cube is not None:
            cube_commands.append(move_action(len(cube_commands), cube, loop))
    await asyncio.gather(*cube_commands)


def main(argv):
    print('search toio core cube')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_and_move(loop))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
