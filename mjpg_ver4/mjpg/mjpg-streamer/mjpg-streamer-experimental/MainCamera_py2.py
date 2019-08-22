import cv2
import numpy as np
import os
import subprocess
import tempfile
import Contours_py2 as Contours
import socket
import time



subprocess.Popen("sh start_uvc.sh", shell = True )

Socket_PORT = 8070
max_users = 5

#####################  Socket Server  ##################################

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('',Socket_PORT))
server_socket.listen(max_users)

connection_socket, addr = server_socket.accept()

while True:
	msg = connection_socket.recv(6)
	print(msg.decode("utf-8"))
	
	if msg == "Exit":
		subprocess.Popen(args = ["fuser", "-k", "-n", "tcp", "8080"], shell = False )
		subprocess.Popen("^C", shell = True )
		time.sleep(1)		
		break


subprocess.Popen(args = ["sh", "start_opencv.sh"], shell = False )

connection_socket.send('Start'.encode('utf-8'))
server_socket.close()
	

