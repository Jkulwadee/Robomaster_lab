import cv2
import numpy as np
import matplotlib.pyplot as plt
width = 640
height = 360
dim = (width, height)
#cv2.IMREAD_GRAYSCALE
load_img = cv2.imread('image/img2.jpg')
img = cv2.resize(load_img, dim, interpolation = cv2.INTER_AREA)

result = img.copy()
image = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
lower = np.array([150,25,0])
upper = np.array([179,255,255])
mask = cv2.inRange(image, lower, upper)
result = cv2.bitwise_and(result, result, mask=mask)

cv2.imshow('mask', mask)
cv2.imshow('result', result)

cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()