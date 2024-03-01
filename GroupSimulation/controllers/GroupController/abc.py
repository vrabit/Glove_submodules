import numpy as np
from controller import Robot, Keyboard
import math

# PID controller parameters
past_vx_error = 0.0
past_vy_error = 0.0
past_alt_error = 0.0
past_pitch_error = 0.0
past_roll_error = 0.0
altitude_integrator = 0.0
last_time = 0.0

def pid(dt, desired_vx, desired_vy, desired_yaw_rate, desired_altitude, actual_roll, actual_pitch, actual_yaw_rate,
        actual_altitude, actual_vx, actual_vy):
    # Velocity PID control (converted from Crazyflie c code)
    gains = {"kp_att_y": 1, "kd_att_y": 0.5, "kp_att_rp": 0.5, "kd_att_rp": 0.1,
             "kp_vel_xy": 2, "kd_vel_xy": 0.5, "kp_z": 10, "ki_z": 5, "kd_z": 5}

    global past_vx_error, past_vy_error, past_alt_error, past_pitch_error, past_roll_error, altitude_integrator

    # Velocity PID control
    vx_error = desired_vx - actual_vx
    vx_deriv = (vx_error - past_vx_error) / dt
    vy_error = desired_vy - actual_vy
    vy_deriv = (vy_error - past_vy_error) / dt
    desired_pitch = gains["kp_vel_xy"] * np.clip(vx_error, -1, 1) + gains["kd_vel_xy"] * vx_deriv
    desired_roll = -gains["kp_vel_xy"] * np.clip(vy_error, -1, 1) - gains["kd_vel_xy"] * vy_deriv
    past_vx_error = vx_error
    past_vy_error = vy_error

    # Altitude PID control
    alt_error = desired_altitude - actual_altitude
    alt_deriv = (alt_error - past_alt_error) / dt
    altitude_integrator += alt_error * dt
    alt_command = gains["kp_z"] * alt_error + gains["kd_z"] * alt_deriv + \
        gains["ki_z"] * np.clip(altitude_integrator, -2, 2) + 48
    past_alt_error = alt_error

    # Attitude PID control
    pitch_error = desired_pitch - actual_pitch
    pitch_deriv = (pitch_error - past_pitch_error) / dt
    roll_error = desired_roll - actual_roll
    roll_deriv = (roll_error - past_roll_error) / dt
    yaw_rate_error = desired_yaw_rate - actual_yaw_rate
    roll_command = gains["kp_att_rp"] * np.clip(roll_error, -1, 1) + gains["kd_att_rp"] * roll_deriv
    pitch_command = -gains["kp_att_rp"] * np.clip(pitch_error, -1, 1) - gains["kd_att_rp"] * pitch_deriv
    yaw_command = gains["kp_att_y"] * np.clip(yaw_rate_error, -1, 1)
    past_pitch_error = pitch_error
    past_roll_error = roll_error

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

if __name__ == '__main__':
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

        key = keyboard.getKey()

        if key == Keyboard.UP:
            forward_desired += 0.5
        elif key == Keyboard.DOWN:
            forward_desired -= 0.5
        elif key == Keyboard.RIGHT:
            sideways_desired -= 0.5
        elif key == Keyboard.LEFT:
            sideways_desired += 0.5
        elif key == ord('Q'):
            yaw_desired = +1
        elif key == ord('E'):
            yaw_desired = -1
        elif key == ord('W'):
            height_diff_desired = 0.1
        elif key == ord('S'):
            height_diff_desired = -0.1

        height_desired += height_diff_desired * dt

        # PID velocity controller with fixed height
        motor_power = pid(dt, forward_desired, sideways_desired,
                          yaw_desired, height_desired,
                          roll, pitch, yaw_rate,
                          altitude, v_x, v_y)

        m1_motor.setVelocity(-motor_power[0])
        m2_motor.setVelocity(motor_power[1])
        m3_motor.setVelocity(-motor_power[2])
        m4_motor.setVelocity(motor_power[3])

        past_time = robot.getTime()
        past_x_global = gps.getValues()[0]
        past_y_global = gps.getValues()[1]

