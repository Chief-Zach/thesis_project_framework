import time
import requests
from hashlib import sha256

cookies = {"user": "ba5d2379-bfcc-4d2b-ba8c-5fc7064f1905"} # Cookie taken from the website under my user

headers = {
    'Content-Type': 'application/json',
}

payload = {
    "Password": "Welcome"
}

response = requests.post("http://127.0.0.1:8000/games/welcome_game/verify", headers=headers, cookies=cookies,
                         json=payload)

print(response, response.text)