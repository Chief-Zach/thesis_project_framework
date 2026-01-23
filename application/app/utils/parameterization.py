import json

from ..utils.aes_service import aes_service, hashing_service
from ..config import get_config
import os
from typing import List, Dict, Any
import secrets
import string

class Parameterization:
    def __init__(self):
        self.config = get_config()
        self.split_key = self._generate_random_string(15)

    def parameterize_flag(self, user_parameter: str, level_parameter: str, *args):
        if not self.config.PARAMETERIZE:
            return hashing_service.hash(level_parameter).hexdigest()

        additional_args = ""
        additional_args_bytes = b''
        for arg in args:
            if isinstance(arg, str):
                additional_args += arg
            elif isinstance(arg, bytes):
                additional_args_bytes += arg
            else:
                raise Exception("Additional args to parameterization must be either str or bytes")

        additional_args_bytes += additional_args.encode()
        encrypted = aes_service.encrypt(user_parameter.encode() + level_parameter.encode() + additional_args_bytes)
        hashed = hashing_service.hash(encrypted).hexdigest()
        return hashed

    @staticmethod
    def _generate_random_string(length):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

    def parameterize_with_data(self, user_cookie, data: Dict[str, Any]):

        padded_page = self._generate_random_string(12) + user_cookie + self.split_key + json.dumps(data) + self._generate_random_string(14)

        return aes_service.encrypt(padded_page.encode())

    def get_data_from_parameterization(self, encrypted_string: str):
        decrypted = aes_service.decrypt(encrypted_string)

        stripped = decrypted[12:-14]

        raw_data = stripped.split(self.split_key)

        input_data = json.loads(raw_data[1])

        return {"cookie": raw_data[0], "input_data": input_data}



parameterization = Parameterization()