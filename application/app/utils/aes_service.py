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
        """
        :arg
        data: String data to hash
        :return:
        Bytes of hashed data. Must be hex digested to turn into a string
        """
        return self.hashing.new(data.encode())

hashing_service = SHA256Service()

class AESService:
    def __init__(self):
        self.key = hashing_service.hash(os.getenv("AES_PASSWORD")).digest()

    def encrypt(self, data: bytes):
        """
        :arg
        data: Data to encrypt as bytes

        :return:
        Encrypted data as a string
        """
        cipher = AES.new(self.key, AES.MODE_SIV)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return base64.b64encode(tag + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data):
        """
        :arg
        encrypted_data: Encrypted data string from encrypt function

        :return:
        Decrypted data string
        """
        raw = base64.b64decode(encrypted_data)

        tag = raw[:16]
        ciphertext = raw[16:]

        cipher = AES.new(self.key, AES.MODE_SIV)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode('utf-8')

aes_service = AESService()