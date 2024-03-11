import asyncio
import logging
import time

import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

import keyboard

URI = 'radio://0/80/2M'

logging.basicConfig(level=logging.ERROR)


async def test():
    while True:
        print('test loop')
        await asyncio.sleep(0.1)


async def handle_client(reader, writer):
    try:
        while True:
            data = await reader.read(1024)  # Adjust buffer size as needed
            if not data:
                break

            message = str.split(data.decode(encoding='utf-8'))
            if writer:
                writer.write(data)  # Echo back to client
                await writer.drain()  # Ensure that the data is actually written to the client

            print(message)

        if writer:
            writer.close()

    except Exception:
        print('caught runtime')
        raise SystemExit("exit")


async def drone():
    cflib.crtp.init_drivers(enable_debug_driver=False)

    scf = SyncCrazyflie(URI)
    scf.__enter__()

    mc = MotionCommander(scf)
    mc.__enter__()

    print('Taking off!')
    await asyncio.sleep(1)

    while True:
        if keyboard.is_pressed('up'):
            print('Moving forward')
            mc.forward(0.5)
            await asyncio.sleep(1)  # Pause for 1 second after each movement
        elif keyboard.is_pressed('down'):
            print('Moving backward')
            mc.back(0.5)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('left'):
            print('Moving left')
            mc.left(0.5)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('right'):
            print('Moving right')
            mc.right(0.5)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('w'):
            print('Moving up 0.2m')
            mc.up(0.2)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('s'):
            print('Moving down 0.2m')
            mc.down(0.2)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('a'):
            print('Yaw left')
            mc.turn_left(90, 72)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('d'):
            print('Yaw right')
            mc.turn_right(90, 72)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('z'):
            print('Taking off')
            mc.take_off(0.2)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('x'):
            print('Landing')
            mc.land(0.2)
            await asyncio.sleep(1)
        elif keyboard.is_pressed('n'):
            print('Performing a trick')
            mc.circle_right(0.5, velocity=0.5, angle_degrees=270)
            await asyncio.sleep(1)

        await asyncio.sleep(.5)


async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8877)
    test_task = asyncio.create_task(test())
    drone_task = asyncio.create_task(drone())

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print('Server Closed - Exit')
        finally:
            test_task.cancel()
            drone_task.cancel()


asyncio.run(main())
