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


address_list_demo_cube = ["EA:BE:D7:F2:D1:87", "C9:A5:04:18:EC:5B"]


async def sound(cube, tone):
    sound = bytearray()
    sound.append(0x03)
    sound.append(0x01)
    sound.append(0x01)
    sound.append(40)
    sound.append(tone)
    sound.append(0xff)
    await cube.write_gatt_char(TOIO_SOUND_UUID, sound)


async def motor(cube):
    motor = bytearray()
    motor.append(0x02)
    motor.append(0x01)
    motor.append(0x01)
    motor.append(0x20)
    motor.append(0x02)
    motor.append(0x01)
    motor.append(0x20)
    motor.append(0x40)
    await cube.write_gatt_char(TOIO_MOTOR_UUID, motor)

doremi = [ 0, 2, 4, 5, 7, 9, 11]

async def move_action(cube_id, cube):
    for ct in range(8):
        tone = 48 + (int(ct / len(doremi)) * 12) + doremi[ct % len(doremi)] + doremi[(cube_id * 2)]
        await sound(cube, tone)
        await motor(cube)
        await asyncio.sleep(1)


async def get_connection(device, loop):
    result = False
    if isinstance(device, str):
        address = device
    else:
        address = device.address

    cube = BleakClient(address, loop)
    while result is not True:
        try:
            print('connect to', device)
            result = await cube.connect()
            if result is True:
                print('success')
        except exc.BleakError as e:
            result = await cube.is_connected()
            if result is True:
                print('connected', result)
            else:
                print(e)
                print('try again', result)
                time.sleep(0.5)
    time.sleep(1)

    connected = await cube.is_connected()
    if not connected:
        print('%s is not connected' % address)
        return None
    print('connect to:', address, cube, result)
    return cube


async def search_and_move(loop):
    #devices = await discover(timeout=1.0)
    devices = address_list_demo_cube 
    cube_commands = []
    for btdev in devices:
        cube = await get_connection(btdev, loop)
        if cube is not None:
            cube_commands.append(move_action(len(cube_commands), cube))
    time.sleep(1)
    print("start")
    await asyncio.gather(*cube_commands)
    print("end")


def main(argv):
    print('search toio core cube')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search_and_move(loop))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
