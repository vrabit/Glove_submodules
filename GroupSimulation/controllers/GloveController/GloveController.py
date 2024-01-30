"""GloveController controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
import atexit
from serial import*
from collections import deque
from enum import Enum

serialPort= 'COM3'
baudRate = 19200
ser = Serial(serialPort,baudRate,timeout = 1)

def close_port():
    ser.close()
    
atexit.register(close_port)

class CommandSelect(Enum):
    
    XY = 1
    XZ = 2
    YZ = 3   
    
    @classmethod
    def matchGesture(cls, inputBuffer):
        return cls(2)


def toInt(xRaw):
    flip = 65535
    tempPos = 1 << 15
    if xRaw & tempPos:
        temp =(~(xRaw) & flip) + 1
        return -temp
    else:
        return xRaw
    
def commands(inputBuffer):
    com = CommandSelect.matchGesture(inputBuffer)
    
    if com == CommandSelect.XY:
        print("XY")
    elif com == CommandSelect.XZ:
        print("XZ")
    elif com == CommandSelect.YZ:
        print("YZ")
    else:
        print("stop")            

def main():
    print("test")
    inputBuffer = deque()
    
    print("test")
    while True:
        data = ser.readline()
        
        GyroXRaw = 0
        GyroYRaw = 0
        GyroZRaw = 0
        flexThumb = 0
        flexIndex = 0
        flexMiddle = 0
        flexRing = 0
        flexPinky = 0
        try:
            GyroXRaw = int(data[2:8].decode('utf-8'))
            GyroYRaw = int(data[10:16].decode('utf-8'))
            GyroZRaw = int(data[18:23].decode('utf-8'))
            flexThumb = int(data[27:33].decode('utf-8'))
            flexIndex = int(data[37:43].decode('utf-8'))
            flexMiddle = int(data[47:53].decode('utf-8'))
            flexRing = int(data[57:63].decode('utf-8'))
            flexPinky = int(data[67:73].decode('utf-8'))
            
            flexList = [flexThumb, flexIndex, flexMiddle, flexRing, flexPinky]
            inputBuffer.append(flexList)
            
        except Exception:
            pass
        
        GyroX = toInt(GyroXRaw)
        GyroY = toInt(GyroYRaw)
        GyroZ = toInt(GyroZRaw)
    
        print("X: " , GyroX , "Y: " , GyroY , "Z: " , GyroZ, "F1: ", flexThumb, "F2: ", flexIndex, "F3: ", flexMiddle, "F4: ", flexRing, "F5: ", flexPinky)

        if len(inputBuffer) >= 10:
            commands(inputBuffer)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("keyboard interrupt")
    finally:
        ser.close()