import json
import os

import requests
from bs4 import BeautifulSoup


# This function is just used because I have access to the wordlist.
# The real users should use https://crackstation.net/ or crack the hashes themselves with a tool such as hashcat
def crack_pass(hash_text):
    with open("../src/static/data/passwords.json") as file:
        password_options: dict = json.load(file)
        inverted_passwords = {y:x for x, y in zip(password_options, password_options.values())}
        return inverted_passwords[hash_text]

cookies = {"user": "cb29fa16-c565-4f55-82a6-6d11f02b6488"} # Cookie taken from the website under my user

# Get the required cookie from the frontend
response = requests.get("http://localhost:8000/games/hard_hashing/frontend", cookies=cookies)

cookie = response.cookies.get("cookie", None)

if cookie is not None:
    cookies["cookie"] = cookie
else:
    raise ValueError

# Get the hidden hash that is hidden in the frontend HTML
soup = BeautifulSoup(response.text, 'html.parser')

hidden = soup.find(id='hidden')

hidden_text = hidden.text[13:]

print(hidden_text)

# Use the cracked hash to log in to the website
response = requests.post("http://localhost:8000/games/hard_hashing/login", cookies=cookies,
                         data={"password": crack_pass(hidden_text)})

print(response.text)

# Craft the payload from the text that is returned from login, the user would see this text on their screen
payload = {
    "flag": response.text.split(" ")[-1][:-1]
}

print(payload)

response = requests.post("http://127.0.0.1:8000/games/hard_hashing/verify", json=payload, cookies=cookies)

print(response.json())