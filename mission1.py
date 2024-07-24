from robomaster import robot
import time
import robomaster
#read sensor
def read_sensor(ep_sensor_adaptor):
    
    s1 = ep_sensor_adaptor.get_io(id=2,port=1) #หน้าซ้าย
    s2 = ep_sensor_adaptor.get_io(id=1,port=1) #หน้าขวา
    s3 = ep_sensor_adaptor.get_io(id=2,port=2) #หลังซ้าย
    s4 = ep_sensor_adaptor.get_io(id=1,port=2) #หลังขวา
    print(s1,s2,s3,s4)
    return s1,s2,s3,s4

def sub_data_handler(sub_info):
    distance = sub_info
    print("tof1:{0}".format(distance[0]))

def check_stage(s1,s2,s3,s4):
    stage = 0

    if s2==0 or s4==0 or (s2==0 and s4==0) or (s1==0 and s2==0 and s4==0):
        stage = 1 #ให้ไปทางซ้าย
        # while True:
        #     if s3==0 or (s1==1 and s2==1):
        #         break
    elif s3==0 or s1==0 or (s1 == 0 and s2==0) or (s1==0 and s2==0 and s3==0):
        stage = 2 #ให้ไปทางขวา
    elif (s1==1 and s2==1) or (s1==1 and s2==1 and s3==1 and s4==1):
        stage = 3 #ให้ไปหน้า
    return stage
  
def move(stage,ep_chassis):
    x_val = 0.2
    y_val = 0.2
    z_val = 90
    xy_spd=0.4
    if stage==1:
        return ep_chassis.drive_wheels(w1=10, w2=10, w3=10, w4=10)
        #return ep_chassis.move(x=0, y=-y_val, z=0, xy_speed=xy_spd).wait_for_completed(),print('Move Left')
    elif stage==2:
        return ep_chassis.move(x=0, y=y_val, z=0, xy_speed=xy_spd).wait_for_completed(),print('Move Right')
    elif stage==3:
        return ep_chassis.move(x=x_val, y=0, z=0, xy_speed=xy_spd).wait_for_completed(),print('Front')
    # elif s3==0:
    #     return ep_chassis.drive_wheels(w1=0, w2=15, w3=0, w4=0)

    # elif s4==0:
    #     return ep_chassis.drive_wheels(w1=0, w2=15, w3=0, w4=0)  
    
if __name__ == '__main__':
    #ควบคุมไฟไว ap
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    #ฟังก์ชันล้อของโรโบมาสเตอร์
    ep_chassis = ep_robot.chassis
    
    while True:
        for i in range(10):
            #อ่านเซนเซอร์ 1-4
            ep_sensor_adaptor = ep_robot.sensor_adaptor
            s1,s2,s3,s4 = read_sensor(ep_sensor_adaptor)

            #ตรวจสอบ stage แล้วคืนค่าส่งให้การเคลื่อนที่ move
            stage = check_stage(s1,s2,s3,s4)
            #time.sleep(0.1)

            #ทำการขยับ
            
            print(stage)
            move(stage,ep_chassis)
            time.sleep(1)
            print('i = ',i)    
        
        
        break

    ep_robot.close()