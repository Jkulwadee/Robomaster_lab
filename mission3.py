import time
from turtle import right
import robomaster
from robomaster import robot
import cv2
import numpy as np
from matplotlib import pyplot as plt


def cam(ep_camera):
    
    
    img = ep_camera.read_cv2_image(strategy="newest")[190:720, 350:1100] #Crop รูปจากการเปิดกล้องเป็น [190:720, 350:1100]
    img_rezie = cv2.resize(img, (640,360), interpolation = cv2.INTER_AREA) #Resize รูปภาพเป็น 640x360 Pixel
    result = img_rezie.copy()
    blured = cv2.bilateralFilter(img_rezie,9,75,75) #นำภาพที่ได้มาเบลอ เพื่อลบ Noise ที่รบกวนออก

    vdo = cv2.cvtColor(blured,cv2.COLOR_BGR2HSV)

    # จับสีเหลือง
    area = 0
    lower = np.array([22,235,100])
    upper = np.array([38,255,255])

    full_mask = cv2.inRange(vdo, lower, upper) #ทำการ Maskสีเหลือง โดยจะเห็นแค่ส่วนของไก่ที่เป็นสีเหลือง กลายเป็นสีขาวบนจอแสดงผล
    result = cv2.bitwise_and(result,result,mask=full_mask)
    
    #Detect Regtangle Red point
    contours, hierarchy = cv2.findContours(full_mask, 
										cv2.RETR_TREE, 
										cv2.CHAIN_APPROX_SIMPLE)

     # จับสีส้ม
    lower_2 = np.array([12,180,100])
    upper_2 = np.array([18,255,255])
    
    #Detect Regtangle Orange point
    mask_orange = cv2.inRange(vdo, lower_2, upper_2) #ทำการ Maskสีส้ม โดยจะเห็นแค่ส่วนของไก่ที่เป็นสีเหลือง กลายเป็นสีขาวบนจอแสดงผล
    result_orange = cv2.bitwise_and(result,result,mask=mask_orange)    


    con, hierarchy = cv2.findContours(mask_orange, 
                                    cv2.RETR_TREE, 
                                    cv2.CHAIN_APPROX_SIMPLE)  

    # กำหนดค่า Defult เพื่อที่จะได้มาจัดการกับ Error Before Asssigne
    y = 0
    x = 0
    w = 0
    h = 0

    y2 = 0
    x2 = 0
    w2 = 0
    h2 = 0
    chicken_status = "ready" 
    
    # Function Contours หรือการตรวจจับไก่เหลืองและส้ม เพื่อทำการตีกรอบรอบไก่ และ คำนวณ x y w h พร้อมทั้งหา area 
    if len(contours) != 0:
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 

            if(area > 400): #Area > 400 ให้จับสีเหลืองและทำการตีกรอบ
                x, y, w, h = cv2.boundingRect(contour) 
                if w > 10:
                    result = cv2.rectangle(result, (x, y), 
                                            (x + w, y + h), 
                                            (0, 0, 255), 2) 
                center_x = x +(w/2)
                center_y = y +(h/2)
                
            
        for pix,con in enumerate(con):
            area_x = cv2.contourArea(con)
            x2, y2, w2, h2 = cv2.boundingRect(con) 
           
            
            if w2 > 10 or area_x > 60:
                result_orange = cv2.rectangle(result, (x2, y2), 
                                            (x2 + w2, y2 + h2), 
                                            (255, 255, 255), 2) 

                #เงื่อนไขการตรวจจับไก่เป็นหรือตาย

                if   w2 > h2 :
                    chicken_status = "alive"
                elif y2 < y+(h/1.5)  or w >h or h2 >w2 :
                    chicken_status = "dead"
                    
                    #เมื่อไก่ตาย Dead ก็จะเข้าสู่ เงื่อนไขภายใน ทำการขยับไปข้างหน้าเสมอ พร้อมทั้งเข้าสู่ฟังก์ชั่น move_robot_to_obj  
                    if chicken_status == "dead":
                        ep_chassis.drive_wheels(w1=20, w2=20, w3=20, w4=20)
                        time.sleep(0.1)

                        move_robot_to_obj(x2, y2, w2 ,h2)  #ส่งการทำงานไปยังฟังก์ชัน

                #จากเงื่อนไขด้านบนทั้งสองนำ  chicken_status มาบอกบนรูปว่าไก่เป็นหรือตาย
                cv2.putText(result, chicken_status, (x2, y2), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                (0, 0, 255))

    #แสดงภาพผลลัพธ์
    cv2.imshow('result',result)
    
    #คืนค่า area ไปยังด้านนอกฟังก์ชันนี้
    return area

def read_sensor(ep_sensor_adaptor):
    
    s1 = ep_sensor_adaptor.get_io(id=2,port=1) #หน้าซ้าย
    s2 = ep_sensor_adaptor.get_io(id=1,port=1) #หน้าขวา
    s3 = ep_sensor_adaptor.get_io(id=2,port=2) #หลังซ้าย
    s4 = ep_sensor_adaptor.get_io(id=1,port=2) #หลังขวา

    return s1,s2,s3,s4

#ฟังก์ชันนี้จะพิเศษกว่าแบบปกติ ซึ่งต้องคืนค่า global เพราะมีการใช้ฟังก์ชันภายในแบบ callback 
#ฟังก์ชัน IR Sensor ตรวจวัดระยะทาง
def sub_data_handler(sub_info):
    global sensor_value
    distance = sub_info
    sensor_value = int(distance[0])

def sensor_detect():
    ep_sensor.sub_distance(freq=2, callback=sub_data_handler)
    time.sleep(1)
    ep_sensor.unsub_distance()
#จบฟังก์ชัน IR Sensor

#ประกาศ global right_left เพื่อมาเก็บค่าของการเดินทางของหุ่นยนต์ทางซ้ายและขวาเป็นลิส เพื่อไปใช้ในฟังก์ชันอื่น
global right_left
right_left = []

#ฟังก์ชันการการเดินไปหา object
def move_robot_to_obj(x, y, w, h):
    global sensor_value #Distance
    global right_left #ลิสการขยับซ้ายและขวา
    sensor_detect()
    
    #เงื่อไขในการขยับซ้ายและขวา    
    if sensor_value > 270: #ระยะมากกว่า 270

        if  310> x+(w/2) > 330:
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed() #หยุด
            print("Center")

        elif x+(w/2) > 330:
            print("move right")
            right_left.append("right") #เก็บค่าการขยับ

            ep_chassis.move(x=0, y=0.1, z=0, xy_speed=0.2).wait_for_completed() #ขวา
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed() #หยุดเพื่อไม่ให้ขยับไกลเกิน

        elif 310 > x+(w/2):
            print("move left")
            right_left.append("left")  #เก็บค่าการขยับ

            ep_chassis.move(x=0, y=-0.1, z=0, xy_speed=0.2).wait_for_completed() #ซ้าย
            ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed() #หยุดเพื่อไม่ให้ขยับไกลเกิน

    elif sensor_value < 270: #ระยะน้อยกว่า 270 (เริ่มกระบวนการจับไก่)
        
        ep_chassis.drive_wheels(w1=-20, w2=-20, w3=-20, w4=-20) #ถอยหลัง
        time.sleep(2)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0) #หยุดเพื่อไม่ให้ขยับไกลเกิน

        ep_gripper.open(power=50) #Gripper Open
        time.sleep(2.5)
        ep_gripper.pause()
        
        #ขยับ Servo 1,2 ลง
        ep_servo.moveto(index=1, angle=-50) 
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-100)
        time.sleep(1)
        ep_servo.moveto(index=2, angle=8)
        time.sleep(1)
        
        #พุ่งไปจับไก่
        ep_chassis.move(x=0.35, y=0, z=0, xy_speed=2).wait_for_completed()
        time.sleep(2.5)
        ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()


        ep_gripper.close(power=80)  #Gripper Close
        time.sleep(2.5)
        ep_gripper.pause()
        print(right_left)

        #ReCenter Servo
        ep_servo.moveto(index=2, angle=-10)
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-50)
        time.sleep(1)
        ep_servo.moveto(index=1, angle=-10)
        time.sleep(1)

        #ReCenter การขยับซ้ายขวา
        for i in right_left[::-1]:
            if i == 'right':
                ep_chassis.move(x=0, y=-0.1, z=0, xy_speed=0.2).wait_for_completed()
                ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()
                
            elif i == 'left':
                ep_chassis.move(x=0, y=0.1, z=0, xy_speed=0.2).wait_for_completed()
                ep_chassis.move(x=0, y=0, z=0, xy_speed=0).wait_for_completed()

        s1,s2,s3,s4 = read_sensor(ep_sensor_adaptor)
        
        #เซนเซอร์หน้าขวา เมื่อไม่เท่ากับ 0 ก็ให้ขยับไปข้างหน้าเรื่อยๆ
        while s2 != 0:
            s1,s2,s3,s4 = read_sensor(ep_sensor_adaptor)
            ep_chassis.drive_wheels(w1=20, w2=20, w3=20, w4=20)
            time.sleep(0.1)


        #หลุด while loop ให้ทำการหยุด แล้ว ถอยหลัง แล้ว หยุด
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        ep_chassis.drive_wheels(w1=-15, w2=-15, w3=-15, w4=-15)
        time.sleep(3)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

        #ปล่อยไก่
        ep_gripper.open(power=50)
        time.sleep(2.5)
        ep_gripper.pause()

        #เคลียร์ลิสการขยับซ้ายขวา
        right_left = []
        print(right_left)

        #ทำการหมุนหุ่นไปทางขวา
        ep_chassis.move(x=0, y=0, z=90,z_speed = 70).wait_for_completed()
        time.sleep(2.5)

       

    

if __name__ == '__main__':
    #เรียกใช้ฟังก์ชันบิวอิน พื้นฐานของ Robomaster
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap") #เชื่อมต่อหุ่นผ่านไวไฟ
    ep_camera = ep_robot.camera
    ep_camera.start_video_stream(display=False)

    ep_chassis = ep_robot.chassis
    ep_gripper = ep_robot.gripper
    ep_servo = ep_robot.servo

    ep_sensor_adaptor = ep_robot.sensor_adaptor
    ep_sensor = ep_robot.sensor
    sensor_value = 1000

    #พุ่งไปข้างหน้าในตอนแรกสุด
    ep_chassis.drive_wheels(w1=40, w2=40, w3=40, w4=40)
    time.sleep(0.1)
    right_left = []
    
    #while Loop ในการเรียกใช้ฟังก์ชันทั้งหมดภายในของโปรแกรม
    while (True):
        s1,s2,s3,s4 = read_sensor(ep_sensor_adaptor) #อ่านเซนเซอร์

        #ขยับไปข้างหน้าและหยุด จนกว่าจะเข้าเงื่อนไขของการจับไก่
        ep_chassis.drive_wheels(w1=20, w2=20, w3=20, w4=20)
        time.sleep(0.1)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)

        #เข้าสู่เงื่อนไขการจับไก่ทั้งหมด
        area = cam(ep_camera)  

        #หากไม่เจอไก่แล้วนั้นเมื่อ เซนเซอร์หน้าขวาเจอกำแพงให้หมุนไปทางซ้าย
        if s2 == 0:
            ep_chassis.move(x=0, y=0, z=90,z_speed = 70).wait_for_completed()
            time.sleep(2.5)

        #หลุดจากลูปเมื่อมีการกด อี และทำการปิดโปรแกรมทั้งหมด
        if cv2.waitKey(1) & 0xFF == ord("e"):   
            cv2.destroyAllWindows()
            ep_camera.stop_video_stream()
            ep_robot.close()
            break