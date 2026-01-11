# utils/encryption.py
from cryptography.fernet import Fernet
from flask import current_app

class Encryptor:
    @staticmethod
    def encrypt(data):
        if not data:
            return b''
        f = Fernet(current_app.config['ENCRYPTION_KEY'])
        if isinstance(data, str):
            data = data.encode()
        return f.encrypt(data)

    @staticmethod
    def decrypt(token):
        if not token:
            return b''
        f = Fernet(current_app.config['ENCRYPTION_KEY'])
        return f.decrypt(token)