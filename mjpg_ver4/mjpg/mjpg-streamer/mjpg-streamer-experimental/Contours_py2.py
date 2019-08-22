import numpy as np
import cv2

def makeContour(img,pts_n):
    column = len(img)
    row = len(img[0])

    for i in range(column):
        for j in range(row):
            if list(img[i][j]) == [255,0,0]:
                img[i][j] = [255,255,255]
            else:
                img[i][j] = [0,0,0]


    img_fill = cv2.fillPoly(img, [pts_n], (255,255,255))

    img_gray = cv2.cvtColor(img_fill, cv2.COLOR_BGR2GRAY)

    ret, img_threshold = cv2.threshold(img_gray,127,255,cv2.THRESH_BINARY)
    img_contour = cv2.findContours(img_threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)


    return img_contour

def pointTest(p,contour):
    dist = cv2.pointPolygonTest(contour, p, True)

    if dist >= 0:
        return True
    elif dist < 0:
        return False
