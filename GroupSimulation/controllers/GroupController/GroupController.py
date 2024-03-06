import numpy as np
from controller import Robot, Keyboard
import math


import atexit
import asyncio
from collections import deque

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


# currently not being used since asyncio takes care of ports
def close_ports():
    print('replace with ser.close()')


atexit.register(close_ports)


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


def pid(dt, desired_vx, desired_vy, desired_yaw_rate, desired_altitude, actual_roll, actual_pitch, actual_yaw_rate,
        actual_altitude, actual_vx, actual_vy,setup_values):

    # Velocity PID control (converted from Crazyflie c code)
    gains = {"kp_att_y": 1, "kd_att_y": 0.5, "kp_att_rp": 0.5, "kd_att_rp": 0.1,
             "kp_vel_xy": 2, "kd_vel_xy": 0.5, "kp_z": 10, "ki_z": 5, "kd_z": 5}

    # Velocity PID control
    vx_error = desired_vx - actual_vx
    vx_deriv = (vx_error - setup_values["past_vx_error"]) / dt
    vy_error = desired_vy - actual_vy
    vy_deriv = (vy_error - setup_values["past_vy_error"]) / dt
    desired_pitch = gains["kp_vel_xy"] * np.clip(vx_error, -1, 1) + gains["kd_vel_xy"] * vx_deriv
    desired_roll = -gains["kp_vel_xy"] * np.clip(vy_error, -1, 1) - gains["kd_vel_xy"] * vy_deriv
    setup_values["past_vx_error"] = vx_error
    setup_values["past_vy_error"] = vy_error

    # Altitude PID control
    alt_error = desired_altitude - actual_altitude
    alt_deriv = (alt_error - setup_values["past_alt_error"]) / dt
    setup_values["altitude_integrator"] += alt_error * dt
    alt_command = gains["kp_z"] * alt_error + gains["kd_z"] * alt_deriv + \
        gains["ki_z"] * np.clip(setup_values["altitude_integrator"], -2, 2) + 48
    setup_values["past_alt_error"] = alt_error

    # Attitude PID control
    pitch_error = desired_pitch - actual_pitch
    pitch_deriv = (pitch_error - setup_values["past_pitch_error"]) / dt
    roll_error = desired_roll - actual_roll
    roll_deriv = (roll_error - setup_values["past_roll_error"]) / dt
    yaw_rate_error = desired_yaw_rate - actual_yaw_rate
    roll_command = gains["kp_att_rp"] * np.clip(roll_error, -1, 1) + gains["kd_att_rp"] * roll_deriv
    pitch_command = -gains["kp_att_rp"] * np.clip(pitch_error, -1, 1) - gains["kd_att_rp"] * pitch_deriv
    yaw_command = gains["kp_att_y"] * np.clip(yaw_rate_error, -1, 1)
    setup_values["past_pitch_error"] = pitch_error
    setup_values["past_roll_error"] = roll_error

    # Motor mixing
    m1 = alt_command - roll_command + pitch_command + yaw_command
    m2 = alt_command - roll_command - pitch_command - yaw_command
    m3 = alt_command + roll_command - pitch_command + yaw_command
    m4 = alt_command + roll_command + pitch_command - yaw_command

    # Limit the motor command
    m1 = np.clip(m1, 0, 600)
    m2 = np.clip(m2, 0, 600)
    m3 = np.clip(m3, 0, 600)
    m4 = np.clip(m4, 0, 600)

    return [m1, m2, m3, m4]


async def drone():

    # PID controller parameters
    setup_values = {"past_vx_error" : 0.0, "past_vy_error" : 0.0, "past_alt_error" : 0.0, "past_pitch_error" : 0.0, "past_roll_error" : 0.0, "altitude_integrator" : 0.0}

    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    # Initialize motors
    m1_motor = robot.getDevice("m1_motor")
    m1_motor.setPosition(float('inf'))
    m1_motor.setVelocity(-1)
    m2_motor = robot.getDevice("m2_motor")
    m2_motor.setPosition(float('inf'))
    m2_motor.setVelocity(1)
    m3_motor = robot.getDevice("m3_motor")
    m3_motor.setPosition(float('inf'))
    m3_motor.setVelocity(-1)
    m4_motor = robot.getDevice("m4_motor")
    m4_motor.setPosition(float('inf'))
    m4_motor.setVelocity(1)

    # Initialize Sensors
    imu = robot.getDevice("inertial_unit")
    imu.enable(timestep)
    gps = robot.getDevice("gps")
    gps.enable(timestep)
    gyro = robot.getDevice("gyro")
    gyro.enable(timestep)

    # Get keyboard
    keyboard = Keyboard()
    keyboard.enable(timestep)

    # Initialize variables
    past_x_global = 0
    past_y_global = 0
    past_time = 0

    height_desired = 1

    # Main loop:
    while robot.step(timestep) != -1:
        dt = robot.getTime() - past_time

        # Get sensor data
        roll = imu.getRollPitchYaw()[0]
        pitch = imu.getRollPitchYaw()[1]
        yaw = imu.getRollPitchYaw()[2]
        yaw_rate = gyro.getValues()[2]
        altitude = gps.getValues()[2]

        # Get body fixed velocities
        v_x = ((gps.getValues()[0] - past_x_global) / dt) * math.cos(yaw) + (
                    (gps.getValues()[1] - past_y_global) / dt) * math.sin(yaw)
        v_y = -((gps.getValues()[0] - past_x_global) / dt) * math.sin(yaw) + (
                    (gps.getValues()[1] - past_y_global) / dt) * math.cos(yaw)

        # Initialize values
        forward_desired = 0
        sideways_desired = 0
        yaw_desired = 0
        height_diff_desired = 0

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

        # F gesture - move up and down
        if int(ges) == 1:
            if y_neg:
                height_diff_desired = 0.2
            elif y_pos:
                height_diff_desired = -0.2
            else:
                pass
        # A gesture - rotate left and right
        elif int(ges) == 0:
            if z_pos:
                yaw_desired = +1
            elif z_neg:
                yaw_desired = -1
            else:
                pass
        # H gesture - move forward and back
        elif int(ges) == 3:
            if z_neg:
                forward_desired += 0.5
            elif z_pos:
                forward_desired -= 0.5
            else:
                pass

        # Y gesture - move left and right
        elif int(ges) == 5:
            if x_neg:
                sideways_desired += 0.5
            elif x_pos:
                sideways_desired -= 0.5
            else:
                pass

        height_desired += height_diff_desired * dt

        # PID velocity controller with fixed height
        motor_power = pid(dt, forward_desired, sideways_desired,
                          yaw_desired, height_desired,
                          roll, pitch, yaw_rate,
                          altitude, v_x, v_y, setup_values)

        m1_motor.setVelocity(-motor_power[0])
        m2_motor.setVelocity(motor_power[1])
        m3_motor.setVelocity(-motor_power[2])
        m4_motor.setVelocity(motor_power[3])

        past_time = robot.getTime()
        past_x_global = gps.getValues()[0]
        past_y_global = gps.getValues()[1]

        await asyncio.sleep(0.0005)


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
        close_ports()

asyncio.run(main())