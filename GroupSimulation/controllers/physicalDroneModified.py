
import keyboard
import logging
import time

import asyncio
import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

URI = 'radio://0/80/2M'


logging.basicConfig(level=logging.ERROR)

async def test():
    while True:
        print('test loop')
        await asyncio.sleep(0.1)

async def drone():
    cflib.crtp.init_drivers(enable_debug_driver=False)

    with SyncCrazyflie(URI) as scf:
        
        with MotionCommander(scf) as mc:
            print('Taking off!')
            time.sleep(1)
            

            while True:
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    # move forward
                    if event.name == 'up':
                        mc.forward(0.5)
                        time.sleep(1)
                    ## move backward   
                    elif event.name == 'down':
                        mc.back(0.5)
                        # Wait a bit
                        time.sleep(1)
                    ## move left
                    elif event.name == 'left':
                        mc.left(0.5)
                        # Wait a bit
                        time.sleep(1)
                    ## move right
                    elif event.name == 'right':
                        mc.right(0.5)
                        # Wait a bit
                        time.sleep(1)
                    # move up
                    elif event.name == 'w':
                        print('Moving up 0.2m')
                        mc.up(0.2)
                        time.sleep(1)
                    # move down
                    elif event.name == 's':
                        print('Moving up 0.2m')
                        mc.down(0.2)
                        time.sleep(1)
                    # yaw left
                    elif event.name == 'a':
                        mc.turn_left(90,72)
                        time.sleep(1)
                    # yaw right
                    elif event.name == 'd':
                        mc.turn_right(90,72)
                        time.sleep(1)
                    # rise
                    elif event.name == 'z':
                        mc.take_off(0.2)
                        time.sleep(1)
                    # land
                    elif event.name == 'x':
                        mc.land(0.2)
                        time.sleep(1)
                    # do a trick
                    elif event.name == 'n':
                        mc.circle_right(0.5, velocity=0.5, angle_degrees=270)

                asyncio.sleep(0.00005)
                    
async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8877)
    test_task = asyncio.create_task(test())

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print('Server Closed - Exit')
        finally:
            test_task.cancel()
            
            
asyncio.run(main())