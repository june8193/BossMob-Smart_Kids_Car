import cv2
import numpy as np
import os
import Contours_py3 as Contours
import socket
import time
import webbrowser

frame = 'None'

Server_IP = "169.254.202.201"
Socket_PORT = 8070
Cam_IP = "http://" + Server_IP + ":8080/?action=stream"
Web_URL = "http://169.254.202.203:8000"
#Cam_IP = "http://192.168.43.246:8080/?action=stream"


######################   Socket Communication  #########################

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((Server_IP, Socket_PORT))

############################ Mouse Event Processing ####################################################################
drawing=False
check = False
BB_check = False
BB_s = (0,0)
BB_e = (0,0)
Region = False
mouse_counter = 0
initBB = 'None'  

pts = []
pts_n = np.array(pts)

def mouse(event,x,y,flags,param):
        global pts, pts_n, drawing, check, contour, Region, mouse_counter, initBB, BB_s, BB_e, BB_check, frame

        if event == cv2.EVENT_LBUTTONDOWN:
                if mouse_counter == 1:
                        drawing = True
                elif mouse_counter == 3:
                        BB_s = (x,y)

        elif event == cv2.EVENT_MOUSEMOVE:
                if (drawing == True)and(check == True):
                        temp_pts = [x,y]
                        pts.append(temp_pts)
                elif BB_check == True:
                        BB_e = (x,y)


        elif event == cv2.EVENT_LBUTTONUP:
                if mouse_counter == 0:
                        check = True


                if (drawing == True)and(check == True):
                        pts_n = np.array(pts)
                        np.save("./files/pts_n",pts_n)
                        drawing = False
                        check = False
                        Region = True

                        contour = Contours.makeContour(frame,pts_n)
                        contour = contour[0][0]
                        np.save("./files/contour",contour)
                        #print(contour)



                if mouse_counter == 2:
                        BB_check = True

                elif mouse_counter == 3:
                        BB_e = (x,y)
                        w = BB_e[0] - BB_s[0]
                        h = BB_e[1] - BB_s[1]
                        initBB = (BB_s[0], BB_s[1], w, h)
                        #tracker.init(frame,initBB)
                        BB_check = False


                mouse_counter = mouse_counter + 1




#################################################################################################################33


video = cv2.VideoCapture(Cam_IP)
_,frame = video.read()
cv2.imshow("frame",frame)
cv2.setMouseCallback("frame",mouse)

######################    Loop ##########################################
while True:
        _,frame = video.read()

        if check == True:
                cv2.putText(frame, "Region Setting Mode", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2)

        elif (BB_check == False) and (Region == True):
                cv2.polylines(frame, [pts_n], isClosed = True, color = (255,0,0), thickness = 4)

        elif BB_check == True:
                cv2.putText(frame, "Object Setting Mode", (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2)
                cv2.polylines(frame, [pts_n], isClosed = True, color = (255,0,0), thickness = 4)

                if (BB_s[0] != 0)and(BB_s[1] != 0):
                        cv2.rectangle(frame,BB_s,BB_e,(0,255,0), thickness = 4)

        if mouse_counter == 4:
                break

        cv2.imshow("frame",frame)
        cv2.waitKey(1)

#########################################################################


cv2.imwrite("./files/initFrame.jpg",frame)
np.save("./files/BoundaryBox",initBB)

video.release()

#####################  Sending ############################3#

os.system("send.bat")



######################## Exit #############################
client_socket.send("Exit".encode('utf-8'))
cv2.destroyAllWindows()

##################  OpenCV Start    ##########################

msg = client_socket.recv(8)
msg = msg.decode('utf-8')
print(msg)

if msg == 'Start':
    print(2)
    client_socket.close()
    time.sleep(1)
    webbrowser.open(Web_URL + "/?action=landing")
    #webbrowser.open(Cam_IP)
    



