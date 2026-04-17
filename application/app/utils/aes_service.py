import secrets

from Crypto.Cipher import AES
import os
from dotenv import load_dotenv
import base64
from app.utils.hashing import hashing_service

load_dotenv()


class AESService:
    def __init__(self):
        password = os.getenv("AES_PASSWORD")
        if password is not None:
            self.key = hashing_service.hash(os.getenv("AES_PASSWORD")).digest()
        else:
            self.key = hashing_service.hash(secrets.token_hex(32)).digest()

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