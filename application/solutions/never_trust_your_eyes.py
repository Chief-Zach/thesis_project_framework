import time
import requests
from hashlib import sha256

cookies = {"user": "cb29fa16-c565-4f55-82a6-6d11f02b6488"} # Cookie taken from the website under my user

payload = {
    "flag": "YouWillNeverGuessMe"
}
response = requests.post("http://127.0.0.1:8000/games/never_trust_your_eyes/verify", json=payload, cookies=cookies)

print(response, response.text)