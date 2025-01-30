from controller import Robot

TIME_STEP = 32

robot = Robot()

camera = robot.getDevice("camera")
camera.enable(TIME_STEP)

distance_sensors = []
for i in range(8):
    sensor = robot.getDevice(f"ps{i}")
    sensor.enable(TIME_STEP)
    distance_sensors.append(sensor)

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

MAX_SPEED = 6.28  

COLOR_SEQUENCE = ['#FF0000', '#FFFF00', '#FF00FF', '#A5691E', '#00FF00']  # Red → Yellow → Pink → Brown → Green


dfs_stack = [] 
visited_positions = set() 


WALL_THRESHOLD = 100.0


def detect_color():
    """Detects the color of the wall in front using the camera."""
    image = camera.getImage()
    width = camera.getWidth()
    height = camera.getHeight()

    red = camera.imageGetRed(image, width, int(width / 2), int(height / 2))
    green = camera.imageGetGreen(image, width, int(width / 2), int(height / 2))
    blue = camera.imageGetBlue(image, width, int(width / 2), int(height / 2))
    
    color = f"#{red:02X}{green:02X}{blue:02X}"
    return color


def rotate_robot(direction, speed=MAX_SPEED, duration=2.0):
    """Rotates the robot by a large angle in the specified direction."""

    if direction == "left":
        left_motor.setVelocity(-speed)
        right_motor.setVelocity(speed)
    elif direction == "right":
        left_motor.setVelocity(speed)
        right_motor.setVelocity(-speed)
    
    steps = int(duration * 1000 / TIME_STEP) 
    for _ in range(steps):
        robot.step(TIME_STEP)
    
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)


def move_forward(speed=MAX_SPEED, duration=1.0):
    """Moves the robot forward for a short duration."""
    left_motor.setVelocity(speed)
    right_motor.setVelocity(speed)
    
    steps = int(duration * 1000 / TIME_STEP) 
    for _ in range(steps):
        robot.step(TIME_STEP)
    
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)


def dfs_navigation():
    """Navigates the robot using Depth-First Search (DFS) logic."""
    global dfs_stack

    front_obstacle = (distance_sensors[0].getValue() + distance_sensors[7].getValue()) / 2  
    left_obstacle = (distance_sensors[5].getValue() + distance_sensors[6].getValue()) / 2 
    right_obstacle = (distance_sensors[1].getValue() + distance_sensors[2].getValue()) / 2 
    if front_obstacle > WALL_THRESHOLD:

        if left_obstacle < WALL_THRESHOLD:
            print("Wall ahead, rotating LEFT.")
            rotate_robot("left", duration=2.0) 
            dfs_stack.append("left")
        elif right_obstacle < WALL_THRESHOLD:
            print("Wall ahead, rotating RIGHT.")
            rotate_robot("right", duration=2.0) 
            dfs_stack.append("right")
        else:
            print("Corner detected! Moving backward.")
            move_forward(speed=-MAX_SPEED, duration=1.0)
            if dfs_stack:
                dfs_stack.pop()
    else:
        print("Path clear, moving forward.")
        move_forward(speed=MAX_SPEED, duration=0.5)


def navigate_to_color(target_color):
    """Navigates the robot to the target wall color."""
    while robot.step(TIME_STEP) != -1:
        detected_color = detect_color()
        print(f"Detected Color: {detected_color}")
        
        if detected_color == target_color:
            print(f"Reached {target_color}")
            break 
        
        dfs_navigation()


def execute_sequence():
    """Executes the sequence of navigating to all target colors."""
    for color in COLOR_SEQUENCE:
        print(f"Navigating to {color}")
        navigate_to_color(color)
    print("All colors detected. Stopping robot.")
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

execute_sequence()