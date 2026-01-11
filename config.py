# config.py
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your-super-secret-key-change-in-production-2025'

    # Dummy main URI (required by Flask-SQLAlchemy)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

    # Separate databases
    SQLALCHEMY_BINDS = {
        'doctors': 'sqlite:///' + os.path.join(basedir, 'instance', 'doctors.db'),
        'hospitals': 'sqlite:///' + os.path.join(basedir, 'instance', 'hospitals.db')
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Encryption key for sensitive data (change this in production!)
    ENCRYPTION_KEY = b'-ErCVQEIZbz9s8DwXT0C5Gzx_NEHoIrh5geF2fEJ0e0='  # 32 url-safe base64-encoded bytes
    # Generate with: from cryptography.fernet import Fernet; Fernet.generate_key()