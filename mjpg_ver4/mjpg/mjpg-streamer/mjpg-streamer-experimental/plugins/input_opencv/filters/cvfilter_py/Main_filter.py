import cv2
import numpy as np
import sys
sys.path.insert(0,'/home/jun/mjpg/mjpg-streamer/mjpg-streamer-experimental/')
import Contours_py2 as Contours
import requests
import socket

##################   Streaming Server Info      #################################

streaming_IP = "169.254.202.203"
streaming_Port = "8000"
streaming_cmd = "None"

streaming_URL = "http://" + streaming_IP + ":" + streaming_Port + "/?action="

#################    Control Server Info   #################################

control_IP = "169.254.202.202"
control_PORT = "8000"
inout = 'None'


#############################################################################
initBB = 'None'
tracker = 'None'
initFrame = 'None'
contour = 'None'
pts_n = 'None'

class MyFilter:
    global tracker, contour, pts_n, inout

    def process(self, img):
        '''
            :param img: A numpy array representing the input image
            :returns: A numpy array to send to the mjpg-streamer output plugin
        '''
        global tracker, contour, pts_n, inout
        
        (success, box) = tracker.update(img)

        (x, y, w, h) = [int(v) for v in box]
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), thickness = 4)	# tracking box
        cv2.polylines(img, [pts_n], isClosed = True, color = (255,0,0), thickness = 4)
        center = (int((2*x + w)/2), int(y+h))
        cv2.circle(img,center,4,(0,0,255),4)
                       
        if Contours.pointTest(center,contour) == True:
            if inout == 'None':
                inout = 'in'
            elif inout == 'out':
                inout = 'in'
                streaming_cmd = "in"
                requests.get(streaming_URL + streaming_cmd)
                requests.get("http://" + control_IP + ":" + control_PORT + "/Main_cam/" + "I")
                                                
        elif Contours.pointTest(center,contour) == False:
            cv2.putText(img, "Out!!!!!!!!!!!!", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2)
            if inout == 'None':
                inout = 'out'
            elif inout == 'in':
                inout = 'out'
                streaming_cmd = "out"
                requests.get(streaming_URL + streaming_cmd)
                requests.get("http://" + control_IP + ":" + control_PORT + "/Main_cam/" + "O")
                

                

        return img
        
def init_filter():
    '''
        This function is called after the filter module is imported. It MUST
        return a callable object (such as a function or bound method). 
    '''
    
    global initBB,tracker,initFrame,contour,pts_n, inout
    
    initBB = np.load("./plugins/input_opencv/filters/cvfilter_py/files/BoundaryBox.npy")
    initBB = tuple(initBB)
    initFrame = cv2.imread("./plugins/input_opencv/filters/cvfilter_py/files/initFrame.jpg")
    contour = np.load("./plugins/input_opencv/filters/cvfilter_py/files/contour.npy")
    pts_n = np.load("./plugins/input_opencv/filters/cvfilter_py/files/pts_n.npy")
    	
    tracker = cv2.TrackerCSRT_create()
    tracker.init(initFrame, initBB)
    
    inout = 'None'

    f = MyFilter()
    return f.process

