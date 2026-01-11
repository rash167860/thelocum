# app.py - Final Complete Version with Encrypted Binary Storage in SQLite
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, DoctorUser, HospitalUser, DoctorProfile, DoctorDocument, HospitalProfile, HospitalDocument, Shift, ShiftApplication
from werkzeug.utils import secure_filename
from datetime import datetime as dt
from utils.encryption import Encryptor
import os
import io
import mimetypes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('doctor_'):
            doc_id = int(user_id.split('_')[1])
            return DoctorUser.query.get(doc_id)
        elif user_id.startswith('hospital_'):
            hosp_id = int(user_id.split('_')[1])
            return HospitalUser.query.get(hosp_id)
        return None

    with app.app_context():
        db.create_all()

    # Home
    @app.route('/')
    def home():
        return render_template('homepage.html')

    # Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form['email'].strip()
            password = request.form['password']
            user_type = request.form.get('user_type', 'doctor')

            if user_type == 'doctor':
                user = DoctorUser.query.filter_by(email=email).first()
            else:
                user = HospitalUser.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')

        return render_template('login.html')

    # Register Doctor
    @app.route('/register-doctor', methods=['GET', 'POST'])
    def register_doctor():
        if request.method == 'POST':
            full_name = request.form['fullName']
            years_exp = request.form.get('yearsOfExperience', 0, type=int)
            email = request.form['email'].strip()
            password = request.form['password']
            confirm = request.form['confirmPassword']

            if password != confirm:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('register_doctor'))

            if DoctorUser.query.filter_by(email=email).first():
                flash('Email already registered!', 'error')
                return redirect(url_for('register_doctor'))

            new_doctor = DoctorUser(
                full_name=full_name,
                years_of_experience=years_exp,
                email=email
            )
            new_doctor.set_password(password)
            db.session.add(new_doctor)
            db.session.commit()
            flash('Doctor account created successfully!', 'success')
            return redirect(url_for('login'))

        return render_template('register-doctor.html')

    # Register Hospital
    @app.route('/register-hospital', methods=['GET', 'POST'])
    def register_hospital():
        if request.method == 'POST':
            hospital_name = request.form['hospitalName']
            contact_person = request.form['contactPerson']
            email = request.form['email'].strip()
            password = request.form['password']
            confirm = request.form['confirmPassword']

            if password != confirm:
                flash('Passwords do not match!', 'error')
                return redirect(url_for('register_hospital'))

            if HospitalUser.query.filter_by(email=email).first():
                flash('Email already registered!', 'error')
                return redirect(url_for('register_hospital'))

            new_hospital = HospitalUser(
                hospital_name=hospital_name,
                contact_person=contact_person,
                email=email
            )
            new_hospital.set_password(password)
            db.session.add(new_hospital)
            db.session.commit()
            flash('Hospital account created successfully!', 'success')
            return redirect(url_for('login'))

        return render_template('register-hospital.html')

    # Dashboard
    @app.route('/dashboard')
    @login_required
    def dashboard():
        if isinstance(current_user, DoctorUser):
            return render_template('doctor/dashboard.html')
        else:
            return render_template('hospital/dashboard.html')

    # Hospital Account
    @app.route('/hospital/account', methods=['GET', 'POST'])
    @login_required
    def hospital_account():
        if not isinstance(current_user, HospitalUser):
            return redirect(url_for('dashboard'))

        profile = current_user.profile or HospitalProfile(hospital_id=current_user.id)

        if request.method == 'POST':
            profile.hospital_type = request.form['hospital_type']
            profile.address = request.form['address']
            profile.city = request.form['city']
            profile.state = request.form['state']
            profile.pincode = request.form['pincode']
            profile.phone = request.form['phone']
            profile.alternate_phone = request.form['alternate_phone']
            profile.website = request.form['website']
            profile.number_of_beds = request.form.get('number_of_beds', type=int)
            profile.about = request.form['about']

            if not current_user.profile:
                db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')

        return render_template('hospital/account.html', profile=profile)

    # Hospital Documents
    @app.route('/hospital/documents')
    @login_required
    def hospital_documents():
        if not isinstance(current_user, HospitalUser):
            return redirect(url_for('dashboard'))
        return render_template('hospital/documents.html')

    # Upload Document - HOSPITAL (Encrypted Binary)
    @app.route('/upload-document', methods=['POST'])
    @login_required
    def upload_document():
        if not isinstance(current_user, HospitalUser):
            return redirect(url_for('dashboard'))

        file = request.files['document_file']
        doc_type = request.form['document_type']

        if file and file.filename:
            file_data = file.read()
            encrypted_data = Encryptor.encrypt(file_data)
            file_name = secure_filename(file.filename)

            new_doc = HospitalDocument(
                hospital_id=current_user.id,
                document_type=doc_type,
                file_data_enc=encrypted_data,
                file_name=file_name
            )
            db.session.add(new_doc)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')

        return redirect(url_for('hospital_documents'))

    # Create Shift
    @app.route('/hospital/create-shift', methods=['GET', 'POST'])
    @login_required
    def create_shift():
        if not isinstance(current_user, HospitalUser):
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            shift_date = dt.strptime(request.form['shift_date'], '%Y-%m-%d').date()
            start_time = dt.strptime(request.form['start_time'], '%H:%M').time()
            end_time = dt.strptime(request.form['end_time'], '%H:%M').time()

            new_shift = Shift(
                hospital_id=current_user.id,
                title=request.form['title'],
                specialty=request.form['specialty'],
                shift_date=shift_date,
                start_time=start_time,
                end_time=end_time,
                pay_rate=request.form.get('pay_rate', type=float),
                pay_type=request.form['pay_type'],
                location_ward=request.form['location_ward'],
                requirements=request.form['requirements'],
                is_urgent='is_urgent' in request.form
            )
            db.session.add(new_shift)
            db.session.commit()
            flash('Shift posted successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('hospital/create_shift.html')

    # Hospital Applications
    @app.route('/hospital/applications')
    @login_required
    def hospital_applications():
        if not isinstance(current_user, HospitalUser):
            return redirect(url_for('dashboard'))
        shifts = Shift.query.filter_by(hospital_id=current_user.id).order_by(Shift.posted_at.desc()).all()
        return render_template('hospital/applications.html', shifts=shifts)

    # ==============================
    # DOCTOR ROUTES
    # ==============================

    @app.route('/doctor/jobs')
    @login_required
    def doctor_jobs():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))
        shifts = Shift.query.filter_by(status='Open').all()
        return render_template('doctor/jobs.html', shifts=shifts)

    @app.route('/doctor/apply/<int:shift_id>', methods=['POST'])
    @login_required
    def doctor_apply(shift_id):
        if not isinstance(current_user, DoctorUser):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

        existing = ShiftApplication.query.filter_by(doctor_id=current_user.id, shift_id=shift_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Already applied'})

        app = ShiftApplication(
            doctor_id=current_user.id,
            shift_id=shift_id,
            status='Pending'
        )
        db.session.add(app)
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/doctor/history')
    @login_required
    def doctor_history():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))
        return render_template('doctor/history.html')

    @app.route('/doctor/payment')
    @login_required
    def doctor_payment():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))
        return render_template('doctor/payment.html')

    @app.route('/doctor/profile', methods=['GET', 'POST'])
    @login_required
    def doctor_profile():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))

        profile = current_user.profile or DoctorProfile(doctor_id=current_user.id)

        if request.method == 'POST':
            profile.phone = request.form['phone']
            profile.address = request.form['address']
            profile.city = request.form['city']
            profile.qualifications = request.form['qualifications']
            profile.license_number = request.form['license_number']

            if not current_user.profile:
                db.session.add(profile)
            db.session.commit()
            flash('Profile updated successfully!', 'success')

        return render_template('doctor/profile.html', profile=profile)

    @app.route('/doctor/documents')
    @login_required
    def doctor_documents():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))
        return render_template('doctor/documents.html')

    @app.route('/doctor/upload-document', methods=['POST'])
    @login_required
    def doctor_upload_document():
        if not isinstance(current_user, DoctorUser):
            return redirect(url_for('dashboard'))

        file = request.files['document_file']
        doc_type = request.form['document_type']

        if file and file.filename:
            file_data = file.read()
            encrypted_data = Encryptor.encrypt(file_data)
            file_name = secure_filename(file.filename)

            new_doc = DoctorDocument(
                doctor_id=current_user.id,
                document_type=doc_type,
                file_data_enc=encrypted_data,
                file_name=file_name
            )
            db.session.add(new_doc)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')

        return redirect(url_for('doctor_documents'))

    @app.route('/view-document/<string:user_type>/<int:doc_id>')
    @login_required
    def view_document(user_type, doc_id):
        if user_type == 'hospital':
            doc = HospitalDocument.query.get_or_404(doc_id)
            if doc.hospital_id != current_user.id:
                abort(403)
        elif user_type == 'doctor':
            doc = DoctorDocument.query.get_or_404(doc_id)
            if doc.doctor_id != current_user.id:
                abort(403)
        else:
            abort(404)

        decrypted_data = Encryptor.decrypt(doc.file_data_enc)

        # Detect MIME type (optional, better UX)
        import mimetypes
        mime_type, _ = mimetypes.guess_type(doc.file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'

        return send_file(
            io.BytesIO(decrypted_data),
            download_name=doc.file_name,
            mimetype=mime_type,
            as_attachment=False  # False = inline view, True = download
        )

    # Logout
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
