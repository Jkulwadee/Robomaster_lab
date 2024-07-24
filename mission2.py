import time
import robomaster
from robomaster import robot
import cv2
import numpy as np
from matplotlib import pyplot as plt

from maze import forward

def cam(ep_camera):
    
    img = ep_camera.read_cv2_image(strategy="newest")[190:720, 300:1000]
    img_rezie = cv2.resize(img, (640,360), interpolation = cv2.INTER_AREA)
    result = img_rezie.copy()
    blured = cv2.bilateralFilter(img_rezie,9,75,75)

    vdo = cv2.cvtColor(blured,cv2.COLOR_BGR2HSV)

    # จับสีเหลือง
    # lower = np.array([25,235,100])
    # upper = np.array([35,255,255])
    area = 0
    lower = np.array([22,235,100])
    upper = np.array([38,255,255])
    full_mask = cv2.inRange(vdo, lower, upper)
    result = cv2.bitwise_and(result,result,mask=full_mask)
    
    #Detect Regtangle Red point
    contours, hierarchy = cv2.findContours(full_mask, 
										cv2.RETR_TREE, 
										cv2.CHAIN_APPROX_SIMPLE)

    #Orange
    lower_2 = np.array([12,180,100])
    upper_2 = np.array([18,255,255])

    mask_orange = cv2.inRange(vdo, lower_2, upper_2)
    result_orange = cv2.bitwise_and(result,result,mask=mask_orange)    


    con, hierarchy = cv2.findContours(mask_orange, 
                                    cv2.RETR_TREE, 
                                    cv2.CHAIN_APPROX_SIMPLE)  
    y = 0
    x = 0
    w = 0
    h = 0

    y2 = 0
    x2 = 0
    w2 = 0
    h2 = 0
    chicken_status = "ready" 
    

    if len(contours) != 0:
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 400): 
                x, y, w, h = cv2.boundingRect(contour) 
                if w > 10:
                    result = cv2.rectangle(result, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 255), 2) 
                center_x = x +(w/2)
                center_y = y +(h/2)

                #print("xy",x,y,"wh",w,h)
                
                
                            
        for pix,con in enumerate(con):
            area_x = cv2.contourArea(con)
            x2, y2, w2, h2 = cv2.boundingRect(con) 
           
            
            if w2 > 10 or area_x > 50:
                result_orange = cv2.rectangle(result, (x2, y2), 
                                            (x2 + w2, y2 + h2), 
                                            (255, 255, 255), 2) 
                # print(y,y2)
                if   w2 > h2 :
                    chicken_status = "alive"
                elif y2 < y+(h/1.5)  or w >h or h2 >w2 :
                    chicken_status = "dead"
                    

                    if chicken_status == "dead":
                        ep_chassis.drive_wheels(w1=20, w2=20, w3=20, w4=20)
                        time.sleep(0.1)
                        move_robot_to_obj(x2, y2, w2 ,h2)  

                cv2.putText(result, chicken_status, (x2, y2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                (0, 0, 255))

              
    #ep_chassis.move(x=0.05, y=0, z=0, xy_speed=0.1).wait_for_completed()
    # cv2.imwrite('image/vdo1.jpg', result)
    
    # cv2.imshow("Orange",mask_orange)
    # cv2.imshow("Blur",blured)
    # cv2.imshow('mask',full_mask)
    cv2.imshow('result',result)
    
    return area

def sub_data_handler(sub_info):
    global sensor_value
    distance = sub_info
    sensor_value = int(distance[0])

def sensor_detect():
    ep_sensor.sub_distance(freq=2, callback=sub_data_handler)
    time.sleep(1)
    ep_sensor.unsub_distance()

def move_robot_to_obj(x, y, w, h):
    global sensor_value
    sensor_detect()
    print("Distance",sensor_value)
    
    
    if sensor_value > 270:
        if  310> x+(w/2) > 330:
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()
            print("Center Mother Fucker")
        elif x+(w/2) > 330:
            print("move right")
            print(x+(w/2))
            ep_chassis.move(x=0, y=0.1, z=0, xy_speed=2).wait_for_completed()
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()
        elif 310 > x+(w/2):
            print("move left")
            print(x+(w/2))
            ep_chassis.move(x=0, y=-0.1, z=0, xy_speed=2).wait_for_completed()
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()

    elif sensor_value < 270:
        
        ep_chassis.drive_wheels(w1=-20, w2=-20, w3=-20, w4=-20)
        time.sleep(1)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

        ep_gripper.open(power=50)
        time.sleep(2.5)
        ep_gripper.pause()
        
        ep_servo.moveto(index=1, angle=-50)
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-100)
        time.sleep(1)
        ep_servo.moveto(index=2, angle=8)
        time.sleep(1)
        
        ep_chassis.move(x=0.3, y=0, z=0, xy_speed=1).wait_for_completed()
        time.sleep(2.5)
        ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()


        # 闭合机械爪
        ep_gripper.close(power=50)
        time.sleep(2.5)
        ep_gripper.pause()

        ep_servo.moveto(index=2, angle=-10)
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-50)
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-10)
        time.sleep(1)

        ep_gripper.open(power=50)
        time.sleep(2.5)
        ep_gripper.pause()

        cv2.destroyAllWindows()
        ep_camera.stop_video_stream()
        ep_robot.close()
 
    

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)

    ep_chassis = ep_robot.chassis
    
    ep_gripper = ep_robot.gripper
    ep_servo = ep_robot.servo

    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_sensor = ep_robot.sensor
    sensor_value = 1000
    ep_chassis.drive_wheels(w1=60, w2=60, w3=60, w4=60)
    time.sleep(0.1)
    while (True):
        ep_chassis.drive_wheels(w1=30, w2=30, w3=30, w4=30)
        time.sleep(0.1)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

        area = cam(ep_camera)  
        if cv2.waitKey(1) & 0xFF == ord("e"):   
            cv2.destroyAllWindows()
            ep_camera.stop_video_stream()
            ep_robot.close()
            break