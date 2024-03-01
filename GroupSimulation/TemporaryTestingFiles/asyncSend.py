# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 14:25:40 2024

@author: Doe
"""
import atexit
import asyncio
from collections import deque

#global 
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


def close_ports():
    print('replace with ser.close()')


atexit.register(close_ports)

def toInt(xRaw):
    flip = 65535
    tempPos = 1 << 15
    if xRaw & tempPos:
        temp =(~(xRaw) & flip) + 1
        return -temp
    else:
        return xRaw
    
async def print_directions():
    while True:
        global x_positive, x_negative, y_positive, y_negative, z_positive, z_negative
        
        x_pos = x_neg = y_pos = y_neg = z_pos = z_neg = False
        async with x_positive_lock, x_negative_lock:
            x_pos = x_positive
            x_neg = x_negative
        async with y_positive_lock, y_negative_lock:
            y_pos = y_positive
            y_neg = y_negative
        async with z_negative_lock, z_positive_lock:
            z_pos = z_positive
            z_neg = z_negative
        results = [x_pos, x_neg, y_pos, y_neg, z_pos, z_neg]
        print(results)
        await asyncio.sleep(0.10)
    
async def calc_x_rotation(rotation_buffer):
    sum_rotation = (sum(list(rotation_buffer)) / 10)

    
    global x_positive, x_negative
    async with x_positive_lock:
        async with x_negative_lock:
            if sum_rotation > 90:
                x_positive = True
                x_negative = False
                #print('X-Positive')
            elif sum_rotation < -90:
                x_negative = True
                x_positive = False
                #print('X-negative')
            else:
                pass
                #x_positive = x_negative = False
                #print('-',end= "")
            
async def calc_y_rotation(rotation_buffer):
    sum_rotation = (sum(list(rotation_buffer)) / 10)
    #print(sum_rotation)
    
    global y_positive, y_negative
    async with y_positive_lock:
        async with y_negative_lock:
            if sum_rotation > 90:
                y_positive = True
                y_negative = False
                #print('Y-Positive')
            elif sum_rotation < -90:
                y_negative = True
                y_positive = False
                #print('Y-Negative')
            else:
                pass
                #y_positive = y_negative = False
                #print('-',end= "")
    

async def calc_z_rotation(rotation_buffer):
    sum_rotation = (sum(list(rotation_buffer)) / 10)
    #print(sum_rotation)
    
    global z_positive, z_negative
    async with z_positive_lock:
        async with z_negative_lock:
            if sum_rotation > 90:
                z_positive = True
                z_negative = False
                #print('Z-Positive')
            elif sum_rotation < -90:
                z_negative = True
                z_positive = False
                #print('Z-Negative')
            else:
                pass
                #z_positive = z_negative = False
                #print('-',end= "")


async def collect_x():
    while True:
        global gesture_change_x, x_rotation_buffer, x_positive, x_negative
        async with gesture_change_x_lock:
            if gesture_change_x == True:
                gesture_change_x = False
                async with x_positive_lock, x_negative_lock:
                    x_positive = x_negative = False
                async with x_rotation_buffer_lock:
                    x_rotation_buffer.clear()
        
        
        async with x_rotation_buffer_lock:
            async with gesture_lock: 
                #print(x_rotation_buffer)
                if len(x_rotation_buffer) == 10:
                    #print(gesture)
                    await calc_x_rotation(x_rotation_buffer)    
            
        await asyncio.sleep(0.10)
        
async def collect_y():
    while True:
        global gesture_change_y, y_rotation_buffer, y_positive, y_negative
        async with gesture_change_y_lock:
            if gesture_change_y == True:
                gesture_change_y = False
                async with y_positive_lock, y_negative_lock:
                    y_positive = y_negative = False
                async with y_rotation_buffer_lock:
                    y_rotation_buffer.clear()
        
        
        async with y_rotation_buffer_lock: 
            if len(y_rotation_buffer) == 10:
                #print(gesture)
                await calc_y_rotation(y_rotation_buffer)    
            
        await asyncio.sleep(0.10)

async def collect_z():
    while True:
        global gesture_change_z, z_rotation_buffer, z_positive, z_negative
        async with gesture_change_z_lock:

            if gesture_change_z == True:
                gesture_change_z = False
                async with z_positive_lock, z_negative_lock:
                    z_positive = z_negative = False
                async with z_rotation_buffer_lock:
                    z_rotation_buffer.clear()
        
        #print(z_rotation_buffer)
        async with z_rotation_buffer_lock: 
            if len(z_rotation_buffer) == 10:
                #print(gesture)
                await calc_z_rotation(z_rotation_buffer)    
            
        await asyncio.sleep(0.10)

async def handle_client(reader, writer):
    gyro_scale = (2000/32767) #gyroscopeRange/(2^15-1) range from spec sheet
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
                    print(gesture)
                
            #print(message[0] + " " + message[1] + " " +message[2] + " " + message [3])

            if writer:
                writer.write(data)  # Echo back to client (optional)
                await writer.drain()  # Ensure that the data is actually written to the client
            
            int_gyro = [int(toInt(int(message[1])) * gyro_scale), int(toInt(int(message[2])) * gyro_scale), int(toInt(int(message[3])) * gyro_scale)]
           
            global x_rotation_buffer, y_rotation_buffer, z_rotation_buffer
            async with x_rotation_buffer_lock: 
                x_rotation_buffer.append(int_gyro[0])
                #print(x_rotation_buffer)
            async with y_rotation_buffer_lock:
                y_rotation_buffer.append(int_gyro[1])
                #print(y_rotation_buffer)
            async with z_rotation_buffer_lock:
                z_rotation_buffer.append(int_gyro[2])
                #print(z_rotation_buffer)
            
            #keep track of previous element
            prev = message[0]

            
           
            #await print_directions()
        if writer:
            writer.close()

    except Exception:
        print('caught runtime')
        raise SystemExit("exit")

async def main():   
    try:
        server = await asyncio.start_server(handle_client, '127.0.0.1', 8877)
        collect_x_task = asyncio.create_task(collect_x())
        collect_y_task = asyncio.create_task(collect_y())
        collect_z_task = asyncio.create_task(collect_z())
        pull_data = asyncio.create_task(print_directions())
        
        print("Server started on 127.0.0.1:8877")
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

    except KeyboardInterrupt:
        print('KeyboardInterrupt - EXIT')
    except RuntimeError:
        print('Runtime Exception')
    except Exception as e:
        print(f"Unexpected Exception: {type(e)}")
    finally:
        close_ports()
    
    
asyncio.run(main())
