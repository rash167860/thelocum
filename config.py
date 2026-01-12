import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production-2025'

    # Default DB = doctors (DoctorUser, DoctorProfile, DoctorDocument, ShiftApplication)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DOCTORS_DB_URL')

    # Bind for hospitals (HospitalUser, HospitalProfile, HospitalDocument, Shift)
    SQLALCHEMY_BINDS = {
        'hospitals': os.environ.get('HOSPITALS_DB_URL')
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENCRYPTION_KEY = b'-ErCVQEIZbz9s8DwXT0C5Gzx_NEHoIrh5geF2fEJ0e0='

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)