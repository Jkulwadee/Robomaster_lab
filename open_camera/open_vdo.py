import cv2
import numpy as np
import matplotlib.pyplot as plt

cap = cv2.VideoCapture(0)

while (True):

    check,frame = cap.read() #Checkตรวจสอบค่า และ Frameคือการอ่านค่า
    
    result = frame.copy()
    #ปรับค่าความสว่างขาวดำของรูปภาพในสีที่ต้องการ
    vdo = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower = np.array([155,25,0])
    upper = np.array([179,255,255])
    
    #นำ vdo มาบปรับค่า lower and upeer
    mask = cv2.inRange(vdo,lower,upper)
    #จากนั้นนำค่าของ result เดิมมาวัดทับในตำแหน่งเพื่อแสดงสีที่ต้องการ
    result = cv2.bitwise_and(result,result,mask=mask)
    
    cv2.imshow('output',frame) #แสดงวิดิโอ
    cv2.imshow('mask',mask)
    cv2.imshow('result',result)

    #เมื่อกดตัว e จะจบการทำงาน
    if cv2.waitKey(1) & 0xFF == ord("e"):
        break

cap.release() #ทำการเคลียร์แรม
cv2.destroyAllWindows() #จบการทำงาน
