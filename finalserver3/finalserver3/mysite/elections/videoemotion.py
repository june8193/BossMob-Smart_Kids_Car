import cv2
import time

def emotioncap():
    cap = cv2.VideoCapture('http://192.168.0.30:8080/?action=stream')
    # cap = cv2.VideoCapture('http://192.168.0.30:8080/?action=stream')
    while(cap.isOpened()):
        cap = cv2.VideoCapture('http://192.168.0.30:8080/?action=stream')
        ret,frame = cap.read()

        cv2.imwrite('wowowowowowowowow.png',frame)
        time.sleep(3)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
