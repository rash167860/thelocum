# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.encryption import Encryptor

db = SQLAlchemy()

# ========================
# DOCTOR SIDE (doctors.db)
# ========================

class DoctorUser(UserMixin, db.Model):
    __bind_key__ = 'doctors'
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer, default=0)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('DoctorProfile', backref='user', uselist=False)
    documents = db.relationship('DoctorDocument', backref='doctor')
    applications = db.relationship('ShiftApplication', backref='doctor')

    def get_id(self):
        return f"doctor_{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DoctorProfile(db.Model):
    __bind_key__ = 'doctors'
    __tablename__ = 'doctor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), unique=True)
    phone_enc = db.Column(db.Text)
    address_enc = db.Column(db.Text)
    city = db.Column(db.String(100))
    qualifications = db.Column(db.Text)
    license_number = db.Column(db.String(100))

    @property
    def phone(self):
        return Encryptor.decrypt(self.phone_enc)

    @phone.setter
    def phone(self, value):
        self.phone_enc = Encryptor.encrypt(value)

    @property
    def address(self):
        return Encryptor.decrypt(self.address_enc)

    @address.setter
    def address(self, value):
        self.address_enc = Encryptor.encrypt(value)

class DoctorDocument(db.Model):
    __bind_key__ = 'doctors'
    __tablename__ = 'doctor_documents'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    document_type = db.Column(db.String(100))
    file_data_enc = db.Column(db.LargeBinary)  # Encrypted binary
    file_name = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ShiftApplication(db.Model):
    __bind_key__ = 'doctors'
    __tablename__ = 'shift_applications'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    shift_id = db.Column(db.Integer)  # Hospital side se shift id reference
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Accepted, Rejected
    payment_amount = db.Column(db.Float)
    payment_status = db.Column(db.String(20), default='Pending')


# ========================
# HOSPITAL SIDE (hospitals.db)
# ========================

class HospitalUser(UserMixin, db.Model):
    __bind_key__ = 'hospitals'
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    hospital_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('HospitalProfile', backref='user', uselist=False)
    documents = db.relationship('HospitalDocument', backref='hospital')
    shifts = db.relationship('Shift', backref='hospital')

    def get_id(self):
        return f"hospital_{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HospitalProfile(db.Model):
    __bind_key__ = 'hospitals'
    __tablename__ = 'hospital_profiles'

    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), unique=True)
    hospital_type = db.Column(db.String(50))  # Govt, Private etc.
    address_enc = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    phone_enc = db.Column(db.Text)
    alternate_phone_enc = db.Column(db.Text)
    website = db.Column(db.String(200))
    number_of_beds = db.Column(db.Integer)
    about = db.Column(db.Text)

    @property
    def address(self):
        return Encryptor.decrypt(self.address_enc)

    @address.setter
    def address(self, value):
        self.address_enc = Encryptor.encrypt(value)

    @property
    def phone(self):
        return Encryptor.decrypt(self.phone_enc)

    @phone.setter
    def phone(self, value):
        self.phone_enc = Encryptor.encrypt(value)

    @property
    def alternate_phone(self):
        return Encryptor.decrypt(self.alternate_phone_enc)

    @alternate_phone.setter
    def alternate_phone(self, value):
        self.alternate_phone_enc = Encryptor.encrypt(value)

class HospitalDocument(db.Model):
    __bind_key__ = 'hospitals'
    __tablename__ = 'hospital_documents'

    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    document_type = db.Column(db.String(100))
    file_data_enc = db.Column(db.LargeBinary)  # Encrypted binary
    file_name = db.Column(db.String(200))  # Original filename for display
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Uploaded')

class Shift(db.Model):
    __bind_key__ = 'hospitals'
    __tablename__ = 'shifts'

    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'))
    title = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(100))
    shift_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    duration_hours = db.Column(db.Float)
    pay_rate = db.Column(db.Float)
    pay_type = db.Column(db.String(20))  # Hourly / Fixed
    location_ward = db.Column(db.String(100))
    requirements = db.Column(db.Text)
    is_urgent = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Open')  # Open / Filled / Cancelled
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)