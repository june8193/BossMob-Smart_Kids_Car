from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from math import pi, sqrt, floor, cos, sin

from rplidar import RPLidar as lidar_setup

import requests


############################# server setting ##################################

control_IP="169.254.202.202"
control_PORT="8000"

############################# lidar setting ##################################

PORT_NAME = 'COM4'   ## lidar setting '/dev/ttyUSB0' for rasberrypi 'COM4' for gal book
DMAX = 6000
IMIN = 0
IMAX = 50

################################ path parameters ###########################################

x_end = 5.6
x_scale = 450

x = [0,0.3,1,2.5,4,x_end]
x = np.array(x)
x1 = x_scale*x
x2 = -x_scale*x

x1 = x1.tolist()
x2 = x2.tolist()
x3 = [0,0]

y_end = 4.9
y_scale = 450

y = [0,1.4,3,4,4.5,y_end]
y = np.array(y)
y1 = y_scale*y
y2 = -y_scale*y
y1 = y1.tolist()
y2 = y2.tolist()
y3 = [-270,270]

################################### path ##########################################
f_right = interp1d(x1,y1,kind='cubic')
f_left = interp1d(x2,y1,kind='cubic')
##b_right = interp1d(x1,y2,kind='cubic')
##b_left = interp1d(x2,y2,kind='cubic')
###################################################################################

#xnew = [0,0.5,1,1.5,2,2.5,3,3.5,4]
#xnew = np.array(xnew)
#xnew1 = x_scale*xnew
#xnew2 = -x_scale*xnew
#xnew1 = xnew1.tolist()
#xnew2 = xnew2.tolist()

#plt.figure(figsize=(5, 5))

#plt.plot(xnew1,f_right(xnew1),'-')
#plt.plot(xnew2,f_left(xnew2),'-')
#plt.plot(xnew1,b_right(xnew1),'-')
#plt.plot(xnew2,b_left(xnew2),'-')
#plt.plot(x3,y3,'-')
#plt.plot(lidarx,lidary,'-')

#circle = plt.Circle((0, 0), radius = 30)
#plt.gca().add_patch(circle)


#plt.xlim(-300,300)
#plt.ylim(-300,300)

#plt.show()
############################# tuning parameters ###################################################
curvepathwidth = 700
straightpathwidth = 500
noiseparam = 10
noiseparam_center = 5

detectrange = 2500  #  unit : mm  2300
stoprange = 1600
stoprange_turn=100  # 300
distance_trash = 9999
leftdist = distance_trash
centerdist = distance_trash
rightdist = distance_trash

############################## check parameters ##################################################

flcheck = 0
frcheck = 0
fccheck = 0

oxcheck='init'
cmd='y'


currentmode = 3 ## initial speed mode
speedsignal = 0
stopsignal = 0

############################## main ###################################################
def send(cmd):
    global control_IP, control_PORT

    requests.get("http://"+control_IP+":"+control_PORT+"/lidar/"+cmd)

def isfront_left(x,y,theta):
    global flcheck
    global noiseparam
    global noisefl
    global leftdist
    
    if f_left(x-curvepathwidth/2*cos(theta-pi/2)) >= y-curvepathwidth/2*sin(theta-pi/2) and f_left(x+curvepathwidth/2*cos(theta-pi/2)) <= y+curvepathwidth/2*sin(theta-pi/2):
        noisefl = noisefl+1
        
        if noisefl > noiseparam:
            flcheck = 1
            leftdist = sqrt(x**2+y**2)
##            print('thetal : ',theta)
        else:
            flcheck = 0
            leftdist = distance_trash
            
    if noisefl <= noiseparam:
        flcheck=0
        leftdist = distance_trash

def isfront_right(x,y,theta):
    global frcheck
    global noiseparam
    global noisefr
    global rightdist
 
    if f_right(x+curvepathwidth/2*cos(pi/2-theta)) >= y-curvepathwidth/2*sin(pi/2-theta) and f_right(x-curvepathwidth/2*cos(pi/2-theta)) <= y+curvepathwidth/2*sin(pi/2-theta):
        noisefr = noisefr+1
        
        if noisefr > noiseparam:
            frcheck = 1
            rightdist = sqrt(x**2+y**2)
        else:
            frcheck = 0
            rightdist = distance_trash
            
    if noisefr <= noiseparam:
        frcheck=0
        rightdist = distance_trash

def isfront_center(x,y):
    global fccheck
    global noiseparam_center
    global noisefc
    global centerdist    
    
    if x<=straightpathwidth/2 and x>=-straightpathwidth/2:
        noisefc = noisefc+1
        if noisefc>=noiseparam_center:
            fccheck = 1
            centerdist = sqrt(x**2+y**2)
        else:
            fccheck = 0
            centerdist = distance_trash

    if noisefc <= noiseparam_center:
        fccheck=0
        centerdist = distance_trash

def setspeed(mode):
    global currentmode ## initail value = 3 (mode 3)
    global speedsignal

    if currentmode==3 and mode==3:
        print('no speed change')
        speedsignal = '0'
        currentmode = 3
        
    elif currentmode==3 and mode==1:
        print('speed mode 1')
        speedsignal = '2' ## push speed selection twice
        currentmode = 1

    elif currentmode==1 and mode==1:
        print('no speed change')
        speedsignal = '0'
        currentmode = 1

    elif currentmode==1 and mode==3:
        print('speed mode 3')
        speedsignal = '2' ## push speed selection twice
        currentmode = 3

def update_scan(num, iterator, line):
    global noisefc
    global noisefr
    global noisefl
    global noisest
    
    global fccheck
    global frcheck
    global flcheck
    global stcheck

    global oxcheck
    global speedsignal

    global centerdist
    global leftdist
    global rightdist
    
    noisefc=0
    noisefr=0
    noisefl=0
    noisest=0
    
    radian=0
    theta=0
    thetal=0
    thetar=0
    dist=0

    scan = next(iterator)      ## scan = (quality,angle,distance)
    offsets = np.array([(np.radians(meas[1]), meas[2]) for meas in scan])
    line.set_offsets(offsets)
    intens = np.array([meas[0] for meas in scan])
    line.set_array(intens)

    scan_data=[distance_trash]*180
    
    for (quality,angle,distance) in scan:
        if quality==15 and distance<=detectrange and (angle<=90 or angle>=270) :
            if angle>=270:
                angle=450-angle   ## 360->90, 270->180
            elif angle<=90:
                angle=90-angle    ## 90->0, 0->90
            scan_data[min([179, floor(angle)])]=distance
            
            if scan_data==[distance_trash]*180:
                fccheck=0
                frcheck=0
                flcheck=0
                noisefc=0
                noisefl=0
                noisefr=0
                centerdist=distance_trash
                rightdist=distance_trash
                leftdist=distance_trash
            else:
                for data in enumerate(scan_data):
                    if data[1] != distance_trash:
                        radian = data[0]*pi/180
                        lidarx = data[1]*cos(radian)
                        lidary = data[1]*sin(radian)
                        dist=sqrt(lidarx**2+lidary**2)
                        
                        
                        isfront_center(lidarx,lidary)

                        if radian>=0 and radian<pi/2:
                            thetar = radian
                            if lidarx-curvepathwidth/2*cos(pi/2-thetar)>0 and lidarx+curvepathwidth/2*cos(pi/2-thetar)<x_end*x_scale:
                                isfront_right(lidarx,lidary,thetar)
                        if radian>=pi/2 and radian<pi:
                            thetal = radian
                            if lidarx+curvepathwidth/2*cos(thetal-pi/2)<0 and lidarx-curvepathwidth/2*cos(thetal-pi/2)>-x_end*x_scale:
                                isfront_left(lidarx,lidary,thetal)

                        if noisefr <= noiseparam:
                            frcheck=0
                            rightdist = distance_trash
                        if noisefl <= noiseparam:
                            flcheck=0
                            leftdist = distance_trash
                        if noisefc <= noiseparam:
                            fccheck=0
                            centerdist = distance_trash

    
    if flcheck == 1 and fccheck == 1 and frcheck == 1:
        if oxcheck!='xxx':
            oxcheck='xxx'
            print(oxcheck)
##        else:
##            print(oxcheck)
            
        if leftdist<=stoprange or centerdist<=stoprange or rightdist<=stoprange:
            print('emergency stop! xxx')
            cmd='s'
            send(cmd)
        
    elif flcheck == 1 and fccheck == 1 and frcheck == 0:
        if oxcheck!='xxo':
            print('turn rignt')
            cmd='r'
            send(cmd)
            oxcheck='xxo'
            print(oxcheck)
        if leftdist<=stoprange_turn or centerdist<=stoprange_turn or rightdist<=stoprange:
            print('xoo turn stop!')
            cmd='s'
            send(cmd)
##        else:
##            print(oxcheck)

        
    elif flcheck == 0 and fccheck == 1 and frcheck == 1:
        if oxcheck!='oxx':
            print('turn left')
            cmd='l'
            send(cmd)
            oxcheck='oxx'
            print(oxcheck)
            
        if leftdist<=stoprange or centerdist<=stoprange_turn or rightdist<=stoprange_turn:
            print('oxx turn stop!')
            cmd='s'
            send(cmd)
##        else:
##            print(oxcheck)
            
    elif flcheck == 1 and fccheck == 0 and frcheck == 0:
        if oxcheck!='xoo':
            cmd='a'
##            send(cmd)
            oxcheck='xoo'
            print(oxcheck)

        if leftdist<=stoprange_turn or centerdist<=stoprange_turn or rightdist<=stoprange_turn:
            print('xoo stop!')
            cmd='s'
            send(cmd)
##        else:
##            print(oxcheck)

    elif flcheck == 0 and fccheck == 0 and frcheck ==1:
        if oxcheck!='oox':
            cmd='d'
##            send(cmd)
            oxcheck='oox'
            print(oxcheck)

        if leftdist<=stoprange_turn or centerdist<=stoprange_turn or rightdist<=stoprange_turn:
            print('oox stop!')
            cmd='s'
            send(cmd)
##        else:
##            print(oxcheck)

    elif flcheck == 1 and fccheck == 0 and frcheck == 1:   ## no control effect
        if oxcheck!='xox':
            oxcheck='xox'
            print(oxcheck)
##        else:
##            print(oxcheck)
 
        
    elif flcheck == 0 and fccheck == 1 and frcheck ==0:
        if oxcheck!='oxo':
            oxcheck='oxo'
            print(oxcheck)
        
        if leftdist<=stoprange or centerdist<=stoprange or rightdist<=stoprange:
            print('emergency stop! oxo')
            cmd='s'
            send(cmd)
        
    else:
        if oxcheck!='ooo':
            cmd='y'
            send(cmd)
            oxcheck='ooo'
            print(oxcheck)
            
    return line

############################################## main ###############################################
if __name__ == '__main__':
    
    lidar=lidar_setup(PORT_NAME)

    lidar.clear_input()

    health=lidar.get_health()
    print(health)

    fig = plt.figure()
    ax1 = plt.subplot(111, projection='polar') ## polar coordinate plot 
    line = ax1.scatter([0, 0], [0, 0], s=5, c=[IMIN, IMAX],
                               cmap=plt.cm.Greys_r, lw=0)
    ax1.set_rmax(DMAX)
    ax1.grid(True)

    iterator = lidar.iter_scans()   ## start scan
    ani = animation.FuncAnimation(fig, update_scan,
            fargs=(iterator, line), interval=100)

    plt.show()

    print('lidar stop')

    lidar.stop()
    lidar.stop_motor()












