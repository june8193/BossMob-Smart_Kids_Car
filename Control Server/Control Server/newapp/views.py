from django.shortcuts import render
from django.http import HttpResponse
from pyfirmata import Arduino, util
import time
import requests
import threading

############################## signal info #############################################

## I, O, S : Main in, out
## R, L, S, F, B : keyboard right, left, stop, forward, backward
## N, M

## r, l, s, a, d : lidar right, left, stop, leftban, rightban
## 2 : lidar speed change Tiwce
## y : lidar ooo
############################ Arduino Setting ###########################################

##board = Arduino('COM10')
##
##iterator = util.Iterator(board)
##iterator.start()


############################# Pin Info ##################################################

# SignalBrake = 26   # blue
# SignalSpeed = 21   # green 
# SignalRight = 6   # purple
# SignalLeft = 20   # yellow
# SignalForward = 13   # white
# SignalBackward = 19  # orange

##SignalBrake = board.get_pin('d:2:o')   # blue
###SignalSpeed = board.get_pin('d::o')   # green 
##SignalRight = board.get_pin('d:3:o')   # purple
##SignalLeft = board.get_pin('d:4:o')   # yellow
##SignalForward = board.get_pin('d:5:o')   # white
##SignalBackward = board.get_pin('d:6:o')  # black
############################ Switch Setting ##################################################

IOflag=0
lidarflag=0
adflag=0
aflag=0
dflag=0

prev_dir = 0
prev_ver = 0

################################# three cmd recieve #######################################
cmd_M = 'None'
cmd_L = 'None'
cmd_K = 'None'

prev_cmd_M = 'None'
prev_cmd_L = 'None'
prev_cmd_K = 'None'

############################################################

counter = 0
Exit = False

def Main_cam(request,cmd):
    global SignalBrake, SignalSpeed, SignalRight, SignalLeft, SignalForward, SignalBackward
    global IOflag, lidarflag
    global adflag, aflag, dflag
    global prev_dir, prev_ver
    global cmd_M, cmd_L, cmd_K
    global counter

        
    cmd_M = cmd
    
    if cmd_M=='O':
        IOflag=1
        print('Out')
    
    elif cmd_M=='I':
        IOflag=0
        print('In')

    
    
    return HttpResponse(cmd)



def lidar(request,cmd):
    global SignalBrake, SignalSpeed, SignalRight, SignalLeft, SignalForward, SignalBackward
    global IOflag, lidarflag
    global adflag, aflag, dflag
    global prev_dir, prev_ver
    global cmd_M, cmd_L, cmd_K

    cmd_L = cmd

    if cmd_L=='r' or cmd_L=='l' or cmd_L=='s':
        lidarflag=1
        print('Lidar Signal')
    
    elif cmd_L=='a':
        lidarflag=0
        adflag=1
        aflag=1
        print('a Signal')
        
    elif cmd_L=='d':
        lidarflag=0
        adflag=1
        dflag=1
        print('d Signal')

    elif cmd_L=='y':
        lidarflag=0
        adflag=0
        aflag=0
        dflag=0
        print('ooo Signal')

    
    return HttpResponse(cmd)


def keyboard(request,cmd):
    global SignalBrake, SignalSpeed, SignalRight, SignalLeft, SignalForward, SignalBackward
    global IOflag, lidarflag
    global adflag, aflag, dflag
    global prev_dir, prev_ver
    global cmd_M, cmd_L, cmd_K
    global counter, Exit

    if counter == 0:
        counter = counter + 1
        t1 = threading.Thread(target = control)
        t1.start()

        
    cmd_K = cmd
    
    if cmd_K=='R' or cmd_K=='L' or cmd_K=='S' or cmd_K=='F' or cmd_K=='B' or cmd_K=='N' or cmd_K=='M':
    
        if lidarflag==1:
            lidarflag=1
            print('Lidar first')
            
        if lidarflag==0 and adflag==1:
            lidarflag=0
            adflag=1
            print('ad ban')

        if lidarflag==0 and adflag==0:
            lidarflag=0
            adflag=0
            aflag=0
            dflag=0
            print('Keyboard Signal')

    if cmd_K == 'q':
        Exit = True
        
    
    return HttpResponse(cmd)



def control():
    global SignalBrake, SignalSpeed, SignalRight, SignalLeft, SignalForward, SignalBackward
    global IOflag, lidarflag
    global adflag, aflag, dflag
    global prev_dir, prev_ver
    global cmd_M, cmd_L, cmd_K
    global Exit

    board = Arduino('COM8',baudrate=115200)

    iterator = util.Iterator(board)
    iterator.start()
    
    SignalBrake = board.get_pin('d:2:o')   # blue
    #SignalSpeed = board.get_pin('d::o')   # green 
    SignalRight = board.get_pin('d:3:o')   # purple
    SignalLeft = board.get_pin('d:4:o')   # yellow
    SignalForward = board.get_pin('d:5:o')   # white
    SignalBackward = board.get_pin('d:6:o')  # black
    
    while True:
        if IOflag == 0 and lidarflag == 0:
            ##///////////////////////// speed change //////////////////////////////##
            
##            if cmd_L=='2':
##                print('Speed Change')
##                SignalSpeed.write(1)
##                time.sleep(0.05)
##                SignalSpeed.write(0)
##                time.sleep(0.05)
##                SignalSpeed.write(1)
##                time.sleep(0.05)
##                SignalSpeed.write(0)

            ##///////////////////////// turn right : Keyboard //////////////////////////////##
            if cmd_K=='R' and adflag==0:
                print('RRRRR')
                SignalLeft.write(0)
                time.sleep(0.05)
                SignalRight.write(1)
                time.sleep(0.1)
                prev_ver='R'

            ##/////////////////////////// turn left : Keyboard //////////////////////////////##
            if cmd_K=='L' and adflag==0:
                print('LLLL')
                SignalRight.write(0)
                time.sleep(0.05)
                SignalLeft.write(1)
                time.sleep(0.1)
                prev_ver='L'

            ##/////////////////////////// left ban (a) //////////////////////////////##
            if cmd_K=='L' and aflag==1:
                print('left ban (a)')
                SignalLeft.write(0)
                time.sleep(0.05)
            elif cmd_K=='R' and aflag==1:
                print('RRRRR (a)')
                SignalLeft.write(0)
                time.sleep(0.05)
                SignalRight.write(1)
                time.sleep(0.1)
                prev_ver='R'

            ##/////////////////////////// right ban (d) //////////////////////////////##
            if cmd_K=='R' and dflag==1:
                print('right ban (d)')
                SignalRight.write(0)
                time.sleep(0.05)
            elif cmd_K=='L' and dflag==1:
                print('LLLL (d)')
                SignalRight.write(0)
                time.sleep(0.05)
                SignalLeft.write(1)
                time.sleep(0.1)
                prev_ver='L'

            ##/////////////////////////// stop : Keyboard //////////////////////////////##
            if cmd_K=='S':
                print('SSSS')
                SignalBrake.write(1)

            ##/////////////////////////// forward : Keyboard //////////////////////////////##
            if cmd_K=='F':
                print('FFFF')
                SignalBackward.write(0)
                time.sleep(0.05)
                SignalForward.write(1)
                prev_dir = 'F'

            ##/////////////////////////// backward : Keyboard //////////////////////////////##
            if cmd_K=='B':
                print('BBBB')
                SignalForward.write(0)
                time.sleep(0.05)
                SignalBackward.write(1)
                prev_dir = 'B'

            ##///////////////////////// turn end : Keyboard up//////////////////////////////##
            if cmd_K=='N':
                #print('NNNN')
                SignalRight.write(0)
                SignalLeft.write(0)

            ##///////////////////////// move end : Keyboard up//////////////////////////////##
            if cmd_K=='M':
                #print('MMMM')
                SignalForward.write(0)
                SignalBackward.write(0)
                SignalBrake.write(0)


        ####################### inside & Lidar control #############################
        elif IOflag==0 and lidarflag==1:
            ##/////////////////////////// turn right : lidar //////////////////////////////##
            if cmd_L=='r':
                print('rrrr')
                SignalLeft.write(0)
                time.sleep(0.05)
                SignalRight.write(1)
                
            ##/////////////////////////// turn left : lidar //////////////////////////////##
            if cmd_L=='l':
                print('llll')
                SignalRight.write(0)
                time.sleep(0.05)
                SignalLeft.write(1)

            ##/////////////////////////// stop : lidar //////////////////////////////##
            if cmd_L=='s':
                print('ssss')
                SignalForward.write(0)
                SignalBackward.write(0)
                SignalLeft.write(0)
                SignalRight.write(0)


        ####################### Outside ##########################/
        elif IOflag == 1:
            if prev_dir=='F' and prev_ver=='R':
                print('F & R')
##                SignalBrake.write(1)        
                SignalForward.write(0)
                SignalRight.write(0)
##                time.sleep(5)
                SignalBrake.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #1
                SignalLeft.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #2
                SignalRight.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #3
                SignalLeft.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #4
                SignalRight.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #5
                SignalLeft.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #6
                SignalRight.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

##                while(True):
##                    print('check')
##                    ## request and response In Out
##                    if cmd_M=='I':
##                        print('IIII')
##                        IOflag=0
##                        prev_dir = 0
##                        prev_ver = 0
##                        SignalForward.write(0)
##                        SignalBackward.write(0)
##                        SignalLeft.write(0)
##                        SignalRight.write(0)
##                        break
##                    
##                    elif cmd_M=='O':
##                        print('OOOO')
##                        SignalForward.write(1)
##                        SignalRight.write(1)
##                        time.sleep(3)
##                        SignalForward.write(0)
##                        SignalRight.write(0)
##                        time.sleep(0.1)

            elif prev_dir=='F' and prev_ver=='L':
                print('F & L')
##                SignalBrake.write(1)
                SignalForward.write(0)
                SignalLeft.write(0)
##                time.sleep(5)
                SignalBrake.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #1
                SignalRight.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #2
                SignalLeft.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #3
                SignalRight.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #4
                SignalLeft.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

                SignalBackward.write(1)   #5
                SignalRight.write(1)
                time.sleep(5)
                SignalBackward.write(0)
                SignalRight.write(0)
                time.sleep(0.05)

                SignalForward.write(1)   #6
                SignalLeft.write(1)
                time.sleep(5)
                SignalForward.write(0)
                SignalLeft.write(0)
                time.sleep(0.05)

##                while(True):
##                    print('check')
##                    ## request and response In Out
##                    if cmd_M=='I':
##                        print('IIII')
##                        IOflag=0
##                        prev_dir = 0
##                        prev_ver = 0
##                        SignalForward.write(0)
##                        SignalBackward.write(0)
##                        SignalLeft.write(0)
##                        SignalRight.write(0)
##                        break
##                    
##                    elif cmd_M=='O':
##                        print('OOOO')
##                        SignalForward.write(1)
##                        SignalLeft.write(1)
##                        time.sleep(3)
##                        SignalForward.write(0)
##                        SignalLeft.write(0)
##                        time.sleep(0.1)

            elif prev_dir=='F':
                print('F only')
##                SignalBrake.write(1)
                SignalForward.write(0)
##                time.sleep(5)
                SignalBrake.write(0)
                time.sleep(0.05)
                SignalBackward.write(1)
                time.sleep(3)
                SignalBackward.write(0)

            elif prev_dir=='B':
                print('B only')
##                SignalBrake.write(1)
                SignalForward.write(0)
##                time.sleep(5)
                SignalBrake.write(0)
                SignalForward.write(1)
                time.sleep(3)
                SignalForward.write(0)

        ###################  Exit ##################################
        if Exit == True:
            SignalBrake.write(0)
            #SignalSpeed.write(0)
            SignalRight.write(0)
            SignalLeft.write(0)
            SignalForward.write(0)
            SignalBackward.write(0)

            break
