from controller import Robot,Motor,Keyboard

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# make motors
motor1 = robot.getDevice("m1_motor")  
motor2 = robot.getDevice("m2_motor")  
motor3 = robot.getDevice("m3_motor")  
motor4 = robot.getDevice("m4_motor")  

# Set motor position to make the drone take off
motor1.setPosition(float('inf'))
motor2.setPosition(float('inf'))
motor3.setPosition(float('inf'))
motor4.setPosition(float('inf'))

# initiate motor speed
t = 100
p=10
r=10
y=10



keyboard = Keyboard()
keyboard.enable(timestep)
while robot.step(timestep) != -1:
    
    command = keyboard.getKey()
    if command == Keyboard.UP:
        r +=1
        print("forward")
    elif command == Keyboard.LEFT:
        r-=1
        print("left")
    elif command == Keyboard.RIGHT:
        r+=1
        print("right")
    elif command ==Keyboard.DOWN:
        p-=1
        print("back")
        
    m1 = t-y+p-r
    m2 = t+y+p+r
    m3 = t-y-p+r
    m4 = t+y-p-r
    motor1.setVelocity(m1)
    motor2.setVelocity(m2)
    motor3.setVelocity(m3)
    motor4.setVelocity((m4))
    print(m1, m2, m3,m4)
    
   
      
   
        
   
    
    
 
    