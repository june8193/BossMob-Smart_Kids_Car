
import requests
import json
import time

def emotion():
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

        response = requests.post(face_api_url, params=params,
                                 headers=headers, json={"url": image_url})
        time.sleep(5)
        print(response.json()[0]['faceAttributes']['emotion'])
