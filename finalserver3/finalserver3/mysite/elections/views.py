from django.shortcuts import render
from django.http import HttpResponse
from .models import Candidate
import threading
from . import face
import requests
import json
import time

happiness = ''
anger = ''
neutral = ''

def emotion():
	global happiness
	global anger
	global neutral
	while True:
		subscription_key = '9db4ab1c869c459bbcb45f4fe9581f29'
		assert subscription_key
		face_api_url = 'https://koreacentral.api.cognitive.microsoft.com/face/v1.0/detect'
		image_url = 'https://upload.wikimedia.org/wikipedia/commons/3/37/Dagestani_man_and_woman.jpg'
		headers = {'Ocp-Apim-Subscription-Key': subscription_key}
		params = {
			'returnFaceId': 'false',
			'returnFaceLandmarks': 'false',
			'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,emotion,hair,makeup,occlusion,accessories,blur,exposure,noise',
			}
		response = requests.post(face_api_url, params=params, headers=headers, json={"url": image_url})
		time.sleep(1)
		print(response.json()[0]['faceAttributes']['emotion'])
		happiness = response.json()[0]['faceAttributes']['emotion']['happiness']
		anger = response.json()[0]['faceAttributes']['emotion']['anger']
		neutral = response.json()[0]['faceAttributes']['emotion']['neutral']
# Create your views here.

hostip = "169.254.202.200:8000"
maincamip = '"http://169.254.202.201:8080/?action=stream"'
babycamip = '"http://192.168.0.29:8080/?action=stream"'
ending = ""
testip = 'static/image/view.png'
mainstate =''
babystate =''
i = ''
a = 0
e = 0

t = threading.Thread(target=emotion, args=(), daemon = True)



def index(request):
	global hostip
	global maincamip
	global babycamip
	global testip
	global ending
	global i
	global a
	global e
	global mainstate
	global babystate
	global t
	global happiness
	global anger
	global neutral

	if 'action' in request.GET:
		action = request.GET['action']

		if action=='main':
			msg = i
			e = e+1
			if e%2 ==0:
				ending = '' 
			else:
				ending = ''
			return render(request, 'elections/main.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip, 'testip' : testip, 'ending' : ending, 'mainstate' : mainstate})
		elif action=='baby':
			msg = i
			babystate = neutral
			return render(request, 'elections/baby.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip,'babystate' : babystate})
		elif action=='out':
			i = "OUT"
			msg = i
			babystate = ''
			mainstate = 'Parking'
			return render(request, 'elections/run.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip})
		elif action =='in':
			i = ""
			msg = i
			mainstate = 'Now safe'
			babystate = ''
			return render(request, 'elections/run.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip})
		elif action == 'landing':
			msg = i
			return render(request, 'elections/landing.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip})
		elif action == 'emotion':
			msg = i 
			t.start()
			return render(request, 'election/run.html',{'message':msg})
	else:
		msg = i
		babystate = neutral
		return render(request, 'elections/run.html',{'message': msg, 'hostip': hostip, 'maincamip': maincamip,'babycamip': babycamip, 'babystate' : babystate})
