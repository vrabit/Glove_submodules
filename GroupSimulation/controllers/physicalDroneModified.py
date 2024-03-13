import asyncio
import logging
import time

import keyboard
import numpy as np

import math

from collections import deque


import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander

# global glove variables
QUEUE_SIZE = 10

gesture = 0
gesture_lock = asyncio.Lock()

gesture_change_x = False
gesture_change_x_lock = asyncio.Lock()

gesture_change_y = False
gesture_change_y_lock = asyncio.Lock()

gesture_change_z = False
gesture_change_z_lock = asyncio.Lock()

x_rotation_buffer = deque(maxlen=QUEUE_SIZE)
x_rotation_buffer_lock = asyncio.Lock()
x_positive = x_negative = False
x_positive_lock = asyncio.Lock()
x_negative_lock = asyncio.Lock()

y_rotation_buffer = deque(maxlen=QUEUE_SIZE)
y_rotation_buffer_lock = asyncio.Lock()
y_positive = y_negative = False
y_positive_lock = asyncio.Lock()
y_negative_lock = asyncio.Lock()

z_rotation_buffer = deque(maxlen=QUEUE_SIZE)
z_rotation_buffer_lock = asyncio.Lock()    
z_positive = z_negative = False
z_positive_lock = asyncio.Lock()
z_negative_lock = asyncio.Lock()




logging.basicConfig(level=logging.ERROR)


def to_int(x_raw):
    flip = 65535
    temp_pos = 1 << 15
    if x_raw & temp_pos:
        temp =(~(x_raw) & flip) + 1
        return -temp
    else:
        return x_raw


async def print_directions():
    while True:
        global x_positive, x_negative, y_positive, y_negative, z_positive, z_negative, gesture
        
        # x_pos = x_neg = y_pos = y_neg = z_pos = z_neg = False
        async with x_positive_lock, x_negative_lock:
            x_pos = x_positive
            x_neg = x_negative
        async with y_positive_lock, y_negative_lock:
            y_pos = y_positive
            y_neg = y_negative
        async with z_negative_lock, z_positive_lock:
            z_pos = z_positive
            z_neg = z_negative
        async with gesture_lock:
            ges = gesture
        results = [x_pos, x_neg, y_pos, y_neg, z_pos, z_neg]
        print(f"Rotation: {results}, Gesture: {ges}")
        await asyncio.sleep(0.10)

async def calc_x_rotation(rotation_buffer):
    # take average rotation x plane
    sum_rotation = (sum(list(rotation_buffer)) / 10)
    
    global x_positive, x_negative
    async with x_positive_lock:
        async with x_negative_lock:
            if sum_rotation > 90:
                x_positive = True
                x_negative = False

            elif sum_rotation < -90:
                x_negative = True
                x_positive = False

            else:
                pass
                #x_positive = x_negative = False
                #print('-',end= "")


async def calc_y_rotation(rotation_buffer):
    # take average rotation y plane
    sum_rotation = (sum(list(rotation_buffer)) / 10)
    
    global y_positive, y_negative
    async with y_positive_lock:
        async with y_negative_lock:
            if sum_rotation > 90:
                y_positive = True
                y_negative = False

            elif sum_rotation < -90:
                y_negative = True
                y_positive = False

            else:
                pass
                #y_positive = y_negative = False
                #print('-',end= "")
    

async def calc_z_rotation(rotation_buffer):
    # take average rotation z plane
    sum_rotation = (sum(list(rotation_buffer)) / 10)
    
    global z_positive, z_negative
    async with z_positive_lock:
        async with z_negative_lock:
            if sum_rotation > 90:
                z_positive = True
                z_negative = False

            elif sum_rotation < -90:
                z_negative = True
                z_positive = False

            else:
                pass
                #z_positive = z_negative = False
                #print('-',end= "")


async def collect_x():
    print('x in')
    while True:
        global gesture_change_x, x_rotation_buffer, x_positive, x_negative

        # reset queue if gesture change
        async with gesture_change_x_lock:
            if gesture_change_x:
                gesture_change_x = False
                async with x_positive_lock, x_negative_lock:
                    x_positive = x_negative = False
                async with x_rotation_buffer_lock:
                    x_rotation_buffer.clear()
        
        async with x_rotation_buffer_lock:
            async with gesture_lock:
                if len(x_rotation_buffer) == 10:
                    await calc_x_rotation(x_rotation_buffer)    

        await asyncio.sleep(0.10)


async def collect_y():
    while True:
        global gesture_change_y, y_rotation_buffer, y_positive, y_negative

        # reset queue if gesture change
        async with gesture_change_y_lock:
            if gesture_change_y:
                gesture_change_y = False
                async with y_positive_lock, y_negative_lock:
                    y_positive = y_negative = False
                async with y_rotation_buffer_lock:
                    y_rotation_buffer.clear()

        async with y_rotation_buffer_lock: 
            if len(y_rotation_buffer) == 10:
                await calc_y_rotation(y_rotation_buffer)    
            
        await asyncio.sleep(0.10)


async def collect_z():
    while True:
        global gesture_change_z, z_rotation_buffer, z_positive, z_negative

        # reset queue if gesture change
        async with gesture_change_z_lock:
            if gesture_change_z:
                gesture_change_z = False
                async with z_positive_lock, z_negative_lock:
                    z_positive = z_negative = False
                async with z_rotation_buffer_lock:
                    z_rotation_buffer.clear()

        async with z_rotation_buffer_lock: 
            if len(z_rotation_buffer) == 10:
                await calc_z_rotation(z_rotation_buffer)    
            
        await asyncio.sleep(0.10)


async def handle_client(reader, writer):
    # gyroscopeRange/(2^15-1) range from spec sheet
    gyro_scale = (2000/32767)
    try:
        prev = ""
        while True:
            data = await reader.read(1024)  # Adjust buffer size as needed
            if not data:
                break
                
            message = str.split(data.decode(encoding='utf-8'))
            if message[0] != prev:
                global gesture_change_x, gesture_change_y, gesture_change_z, gesture
                async with gesture_change_x_lock:
                    gesture_change_x = True
                async with gesture_change_y_lock:
                    gesture_change_y = True
                async with gesture_change_z_lock:
                    gesture_change_z = True
                async with gesture_lock:
                    gesture = message[0]
                    #print(gesture)

            if writer:
                writer.write(data)  # Echo back to client 
                await writer.drain()  # Ensure that the data is actually written to the client
            
            # create list of gyro rotation values with scale applied
            int_gyro = [int(to_int(int(message[1])) * gyro_scale), int(to_int(int(message[2])) * gyro_scale), int(to_int(int(message[3])) * gyro_scale)]
           
            # fill the rotation_buffers to be used in approximating rotation
            global x_rotation_buffer, y_rotation_buffer, z_rotation_buffer
            async with x_rotation_buffer_lock: 
                x_rotation_buffer.append(int_gyro[0])

            async with y_rotation_buffer_lock:
                y_rotation_buffer.append(int_gyro[1])

            async with z_rotation_buffer_lock:
                z_rotation_buffer.append(int_gyro[2])
            
            # keep track of previous element
            prev = message[0]

        if writer:
            writer.close()

    except Exception:
        print('caught runtime')
        raise SystemExit("exit")


async def handle_client(reader, writer):
    # gyroscopeRange/(2^15-1) range from spec sheet
    gyro_scale = (2000 / 32767)
    try:
        prev = ""
        while True:
            data = await reader.read(1024)  # Adjust buffer size as needed
            if not data:
                break

            message = str.split(data.decode(encoding='utf-8'))
            if message[0] != prev:
                global gesture_change_x, gesture_change_y, gesture_change_z, gesture
                async with gesture_change_x_lock:
                    gesture_change_x = True
                async with gesture_change_y_lock:
                    gesture_change_y = True
                async with gesture_change_z_lock:
                    gesture_change_z = True
                async with gesture_lock:
                    gesture = message[0]
                    # print(gesture)

            if writer:
                writer.write(data)  # Echo back to client
                await writer.drain()  # Ensure that the data is actually written to the client

            # create list of gyro rotation values with scale applied
            int_gyro = [int(to_int(int(message[1])) * gyro_scale), int(to_int(int(message[2])) * gyro_scale),
                        int(to_int(int(message[3])) * gyro_scale)]

            # fill the rotation_buffers to be used in approximating rotation
            global x_rotation_buffer, y_rotation_buffer, z_rotation_buffer
            async with x_rotation_buffer_lock:
                x_rotation_buffer.append(int_gyro[0])

            async with y_rotation_buffer_lock:
                y_rotation_buffer.append(int_gyro[1])

            async with z_rotation_buffer_lock:
                z_rotation_buffer.append(int_gyro[2])

            # keep track of previous element
            prev = message[0]

        if writer:
            writer.close()

    except Exception:
        print('caught runtime')
        raise SystemExit("exit")


async def drone():
    delay = 1.5
    cflib.crtp.init_drivers(enable_debug_driver=False)
    URI = 'radio://0/80/2M'

    scf = SyncCrazyflie(URI)
    scf.__enter__()

    mc = MotionCommander(scf)
    mc.__enter__()

    print('Taking off!')
    await asyncio.sleep(1)

    while True:

        # update local variables with collected data
        global x_positive, x_negative, y_positive, y_negative, z_positive, z_negative, gesture
        async with x_positive_lock, x_negative_lock:
            x_pos = x_positive
            x_neg = x_negative

        async with y_positive_lock, y_negative_lock:
            y_pos = y_positive
            y_neg = y_negative

        async with z_positive_lock, z_negative_lock:
            z_pos = z_positive
            z_neg = z_negative

        async with gesture_lock:
            ges = gesture


        # H gesture - move forward and back
        if int(ges) == 3:
            if z_neg:
                mc.forward(0.1)
                print('Moving forward')
                await asyncio.sleep(delay)
            elif z_pos:
                mc.back(0.1)
                print('Moving back')
                await asyncio.sleep(delay)
            else:
                pass
              # Pause for 1 second after each movement
        # Y gesture - move left and right
        elif int(ges) == 5:
            if x_neg:
                mc.left(0.1)
                print('Moving left')
                await asyncio.sleep(delay)

            elif x_pos:
                mc.right(0.1)
                print('Moving right')
                await asyncio.sleep(delay)
            else:
                pass

        elif int(ges) == 1:
            if y_neg:
                mc.up(0.2)
                print('Moving up 0.2m')
                await asyncio.sleep(delay)
            elif y_pos:
                mc.down(0.2)
                print('Moving down 0.2m')
                await asyncio.sleep(delay)
            else:
                pass

        # A gesture - rotate left and right
        elif int(ges) == 0:
            if z_pos:
                mc.turn_left(90,72)
                print('rotate left')
                await asyncio.sleep(delay)
            elif z_neg:
                mc.turn_right(90,72)
                print('rotate right')
                await asyncio.sleep(delay)
            else:
                pass

        elif int(ges) == 4:
            if y_pos:
                mc.land(0.2)
                print('Landing')
                await asyncio.sleep(delay)
            elif y_neg:
                mc.take_off(0.2)
                print('Taking off')
                await asyncio.sleep(delay)

        elif keyboard.is_pressed('x'):
            print('Landing')
            mc.land(0.2)


        elif keyboard.is_pressed('n'):
            print('Performing a trick')
            mc.circle_right(0.5, velocity=0.5, angle_degrees=270)


        await asyncio.sleep(0.0005)

async def main():   
    try:
        # create tasks
        server = await asyncio.start_server(handle_client, '127.0.0.1', 8877)
        collect_x_task = asyncio.create_task(collect_x())
        collect_y_task = asyncio.create_task(collect_y())
        collect_z_task = asyncio.create_task(collect_z())
        pull_data = asyncio.create_task(print_directions())
        run_drone = asyncio.create_task(drone())
        print("Server started on 127.0.0.1:8877")

        # when server closes, stop all coroutines
        async with server:
            try:
                await server.serve_forever()
            except asyncio.CancelledError:
                print('Server Closed - Exit')
            finally:
                collect_x_task.cancel()
                collect_y_task.cancel()
                collect_z_task.cancel()
                pull_data.cancel()
                run_drone.cancel()

    except KeyboardInterrupt:
        print('KeyboardInterrupt - EXIT')
    except RuntimeError:
        print('Runtime Exception')
    except Exception as e:
        print(f"Unexpected Exception: {type(e)}")
    finally:
        print('end')

asyncio.run(main())
