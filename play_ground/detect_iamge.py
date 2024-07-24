import time
import robomaster
from robomaster import robot
import cv2
import numpy as np
from matplotlib import pyplot as plt

def sub_data_handler(sub_info):
    distance = sub_info
    print("tof1:{0}".format(distance[0]))



def cam(ep_camera):
    
    img = ep_camera.read_cv2_image(strategy="newest")[190:720, 350:1100]
    img_rezie = cv2.resize(img, (640,360), interpolation = cv2.INTER_AREA)
    result = img_rezie.copy()
    blured = cv2.bilateralFilter(img_rezie,9,75,75)

    vdo = cv2.cvtColor(blured,cv2.COLOR_BGR2HSV)

    # จับสีเหลือง
    # lower = np.array([25,235,100])
    # upper = np.array([35,255,255])
    area = 0
    lower = np.array([25,235,100])
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
    #Black
    lower_3 = np.array([0,0,0])
    upper_3 = np.array([0,0,0])

    mask_black = cv2.inRange(vdo, lower_3, upper_3)
    result_black = cv2.bitwise_and(result,result,mask=mask_black)    


    con_black, hierarchy = cv2.findContours(mask_black, 
                                    cv2.RETR_TREE, 
                                    cv2.CHAIN_APPROX_SIMPLE)  
    y = 0
    x = 0
    w = 0
    h = 0
    chicken_status = 'Ready'
    if len(contours) != 0:
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 400): 
                x, y, w, h = cv2.boundingRect(contour) 
                if w > 10:
                    result = cv2.rectangle(blured, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 255), 2) 
                center_x = x +(w/2)
                center_y = y +(h/2)

                #print("xy",x,y,"wh",w,h)
                
                
                            
        for pix,con in enumerate(con):
            area_x = cv2.contourArea(con)
            x2, y2, w2, h2 = cv2.boundingRect(con) 
           
            
            if w2 > 15 or area_x > 80:
                result_orange = cv2.rectangle(blured, (x2, y2), 
                                            (x2 + w2, y2 + h2), 
                                            (255, 255, 255), 2) 
                # print(y,y2)
                if   w2 > h2 :
                    chicken_status = "alive"
                elif y2 < y+(h/1.5)  or w >h or h2 >w2 :
                    chicken_status = "dead"

                cv2.putText(result, chicken_status, (x2, y2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                (0, 0, 255))

        for pig,con_black in enumerate(con_black):
            area_black = cv2.contourArea(con_black)
            x_b, y_b, w_b, h_b = cv2.boundingRect(con_black) 
           
            
            if area_black > 35 or x_b > 20:
                result_black = cv2.rectangle(result, (x_b, y_b), 
                                            (x_b + w_b, y_b + h_b), 
                                            (0, 0, 0), 2) 
                
                cv2.putText(result, "Your Fucking Goals", (x_b, y_b), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                (0, 0, 0))    
    # cv2.imshow("Orange",mask_orange)
    # cv2.imshow("Blur",blured)
    # cv2.imshow('mask',full_mask)
    cv2.imshow('result',result)
    
    return area

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)

    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_chassis = ep_robot.chassis
    ep_gripper = ep_robot.gripper
    
    while (True):
        
        area = cam(ep_camera)
    
        if cv2.waitKey(1) & 0xFF == ord("e"):   
            cv2.destroyAllWindows()
            ep_camera.stop_video_stream()
            ep_robot.close()
            break
