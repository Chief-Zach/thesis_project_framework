import json

from ..utils.aes_service import aes_service, hashing_service
from ..config import get_config
from typing import List, Dict, Any
import secrets
import string

class Parameterization:
    def __init__(self, config):
        self.config = config
        self.split_key = self._generate_random_string(15)

    def parameterize_flag(self, user_parameter: str, level_parameter: str, *args):
        """
        :arg
        user_parameter: Users cookie in the form of a string
        level_parameter: The unique level code provided by the framework
        *args: Any other string or byte types to provide more randomness to the flag
        --
        :returns
        Custom user flag string
        """
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
        """
        :arg
        user_cookie: Users cookie in the form of a string
        data: The data to encrypt in the form of a dictionary
        --
        :returns
        AES encrypted string
        """

        padded_page = self._generate_random_string(12) + user_cookie + self.split_key + json.dumps(data) + self._generate_random_string(14)

        return aes_service.encrypt(padded_page.encode())

    def get_data_from_parameterization(self, encrypted_string: str):
        """
        :arg
        encrypted_string: The AES encrypted string from the parameterize_with_data function
        --
        :returns
        Dictionary with the following structure:
        {
            cookie: User cookie that parameterized data
            input_data: The data dictionary that was encrypted
        }
        """

        decrypted = aes_service.decrypt(encrypted_string)

        stripped = decrypted[12:-14]

        raw_data = stripped.split(self.split_key)

        input_data = json.loads(raw_data[1])

        return {"cookie": raw_data[0], "input_data": input_data}
