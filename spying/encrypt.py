from cryptography.fernet import Fernet
from os import listdir
from os.path import isfile, join
from typing import Tuple, Callable


class Encryptor:
    """
    class for encrypting and decrypting files and directories
    """
    def __init__(self, key=None):
        self.encryption_key = key.encode() if key else Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def encrypt_file(self, path) -> bool:
        """
        Encrypt one file and return whether succeeded or not
        """
        try:
            with open(path, 'rb') as f:
                original = f.read()
            encrypted = self.fernet.encrypt(original)
            with open(path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted)
        except OSError:
            return False
        return True

    def _doall(self, path: str, func: Callable[[str], bool]) -> Tuple[list, list]:
        """
        (worked, didn't)
        @type func: function that gets a path and return bool
        """
        if isfile(path):
            if func(path):
                return [path], []
            return [], [path]
        s = ([], [])
        for f in listdir(path):
            t = self._doall(join(path, f), func)
            s[0].extend(t[0])
            s[1].extend(t[1])
        return s

    def encrypt(self, path: str) -> Tuple[list, list]:
        """
        return a list of all the files it encrypted and a list of all the paths it didn't succeed to encrypt
        """
        return self._doall(path, self.encrypt_file)

    def decrypt_file(self, path: str) -> bool:
        """
        decrypt one file and return whether succeeded or not
        """
        try:
            with open(path, 'rb') as encrypted_file:
                encrypted = encrypted_file.read()
            decrypted = self.fernet.decrypt(encrypted)
            with open(path, 'wb') as decrypted_file:
                decrypted_file.write(decrypted)
            return True
        except OSError:
            return False

    def decrypt(self, path: str) -> Tuple[list, list]:
        """
        return a list of all the files it decrypted and a list of all the paths it didn't succeed to decrypt
        """
        return self._doall(path, self.decrypt_file)
