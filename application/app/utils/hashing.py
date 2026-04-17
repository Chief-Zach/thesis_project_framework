from Crypto.Hash import SHA256
from Crypto.Hash.SHA256 import SHA256Hash

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

    def str_hash(self, data: str) -> str:
        """
        :arg
        data: String data to hash
        :return:
        Hex digested hash
        """
        return self.hashing.new(data.encode()).hexdigest()


hashing_service = SHA256Service()
