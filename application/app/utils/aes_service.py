from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import os

from Crypto.Hash.SHA256 import SHA256Hash
from dotenv import load_dotenv
import base64

load_dotenv()

class SHA256Service:
    def __init__(self):
        self.hashing = SHA256.new()
    def hash(self, data: str) -> SHA256Hash:
        return self.hashing.new(data.encode())

hashing_service = SHA256Service()

class AESService:
    def __init__(self):
        self.key = hashing_service.hash(os.getenv("AES_PASSWORD")).digest()

    def encrypt(self, data: bytes):
        cipher = AES.new(self.key, AES.MODE_SIV)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return base64.b64encode(tag + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data):
        raw = base64.b64decode(encrypted_data)

        tag = raw[:16]
        ciphertext = raw[16:]

        cipher = AES.new(self.key, AES.MODE_SIV)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

aes_service = AESService()