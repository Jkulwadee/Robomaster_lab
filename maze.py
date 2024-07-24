from itertools import count
import cv2
import robomaster
from robomaster import robot
from robomaster import vision
import numpy as np
import time

def forward():
    ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
    print("forward")
    time.sleep(1)

def backward():
    ep_chassis.drive_wheels(w1=speed, w2=speed, w3=speed, w4=speed)
    time.sleep(5)
    print("backward")

def stop():
    ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()
    time.sleep(1)

def go_left():
    ep_chassis.move(x=0, y=-y_val, z=0, xy_speed=0).wait_for_completed()
    print("left")

def go_right():
    ep_chassis.move(x=0, y=y_val, z=0, xy_speed=0).wait_for_completed()
    print("right")

def turn(symbol):
    ep_chassis.move(x=0, y=0, z=symbol*z_val + 2, z_speed=90).wait_for_completed()

def current_cell(maz_dis):
    return maz_dis // 4

if __name__ == "__main__":
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_vision = ep_robot.vision
    ep_camera = ep_robot.camera
    ep_chassis = ep_robot.chassis
    ep_sensor = ep_robot.sensor
    ep_servo = ep_robot.servo
    ep_gripper = ep_robot.gripper

    speed = 25
    x_val = 0.1
    y_val = 0.05
    z_val = 90
    left_right = 1
    turn_status = 0
    maz_dis = 0
    row = 1

    counts = 0
    while True:
        # for i in range(5):
        print(current_cell(maz_dis), row)
        if turn_status == 0:
            if maz_dis == 21:

                if counts == 2:
                    stop()
                    break

                turn(left_right)
                turn_status = 1
                maz_dis = 0

            else:
                maz_dis += 1
                forward()
                print(maz_dis)

        elif turn_status == 1:
            if maz_dis == 6:
                # stop()
                turn(left_right)
                left_right *= -1
                row += 1
                turn_status = 2
                maz_dis = 0
            else:
                maz_dis += 1
                forward()
                print(maz_dis)
        
        elif turn_status == 2:
            # turn(-1)
            maz_dis = 0
            turn_status = 0
            counts += 1
            
            

    cv2.destroyAllWindows()
    ep_robot.close