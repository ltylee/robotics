import cv2
import numpy as np

frameWidth = 640
frameHeight = 480

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
cap.set(10,30)
cap.set(cv2.CAP_PROP_FPS,1000)


myColors = [[21,48,109,51,255,255]]
myColorValues = [[0,0,255]]

myPoints = []

def findColor(img):
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    for color,penColor in zip(myColors,myColorValues):
        lower = np.array(color[:3])
        upper = np.array(color[3:6])
        mask = cv2.inRange(imgHSV,lower,upper)
        centers = getContours(mask)
        for center in centers:
            x = center[0]
            y = center[1]
            if x != 0 and y != 0:
                myPoints.append([x,y,penColor])
        #cv2.circle(imgResult,(x,y),10,penColor,cv2.FILLED)


def getContours(img):
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    centers = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            #cv2.drawContours(imgResult, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
            x, y, w, h = cv2.boundingRect(approx)
            centers.append([x+w//2,y+h//2])
    return centers

def drawOnCanvas(myPoints):
    for i in range(len(myPoints)-1):
        point1 = myPoints[i]
        point2 = myPoints[i+1]
        cv2.line(imgResult,point1[:2],point2[:2],point1[2],3)

while True:
    success, img = cap.read()
    imgResult = img.copy()
    findColor(img)
    drawOnCanvas(myPoints[-100:])
    cv2.imshow("Video",imgResult)
    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break