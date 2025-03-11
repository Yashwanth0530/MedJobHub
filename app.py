from flask import Flask,send_from_directory, render_template, request, jsonify, redirect, send_file, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime
from flask_mail import Mail, Message
from random import randint
import secrets
import os
from flask import session
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import re,traceback


app = Flask(__name__)

upload_folder = 'uploads'
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)

app.config['UPLOAD_FOLDER'] = upload_folder  # Make sure this directory exists
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'jpg', 'png'}

# Helper function to check allowed file types
def allowed_file(filename):
    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "medjobhub1234@gmail.com"
app.config['MAIL_PASSWORD'] = "taen vhzs yuja fztl"  # Use App Password if needed
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Generate and set the secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users1.db'
db = SQLAlchemy(app)
with app.app_context():
    db.drop_all()  # This will drop all tables in the database
    db.create_all()  # Recreate tables based on current models
app.secret_key = os.urandom(24)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    # Establish a relationship with the additional details
    additional_details = db.relationship('UserProfile', backref='user', uselist=False)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_pic_url = db.Column(db.String(200))  # URL for the profile picture
    website = db.Column(db.String(200))  # Social media links
    github = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    skills = db.Column(db.String(500), nullable=True) # Can be used for user skills
    education = db.Column(db.Text)  # Education details
    # New fields for storing file information
    education_file = db.Column(db.String(200))  # Path to the uploaded file
    education_filename = db.Column(db.String(200)) 
    work_experience = db.Column(db.Text)  # Work experience details
    certifications = db.Column(db.Text)

otp_storage = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/jobs', methods=['GET'])
def jobs():
    return render_template('jobs.html')

# JOBS
@app.route('/jobs/supspec', methods=['GET'])
def supspec():
    return render_template('jobs/sup_spec.html')

@app.route('/jobs/mddoc', methods=['GET'])
def mddoc():
    return render_template('jobs/md_doc.html')

@app.route('/jobs/mbbs', methods=['GET'])
def mbbs():
    return render_template('jobs/mbbs.html')

@app.route('/jobs/admin', methods=['GET'])
def admin():
    return render_template('jobs/admin.html')

@app.route('/jobs/ambulance', methods=['GET'])
def ambulance():
    return render_template('jobs/ambulance.html')

@app.route('/jobs/bams', methods=['GET'])
def bams():
    return render_template('jobs/bams.html')

@app.route('/jobs/dentist', methods=['GET'])
def dentist():
    return render_template('jobs/dentist.html')

@app.route('/jobs/frontoffice', methods=['GET'])
def frontoffice():
    return render_template('jobs/frontoffice.html')

@app.route('/jobs/insurance', methods=['GET'])
def insurance():
    return render_template('jobs/insurance.html')

@app.route('/jobs/labt', methods=['GET'])
def labt():
    return render_template('jobs/lab_t.html')

@app.route('/jobs/medrep', methods=['GET'])
def medrep():
    return render_template('jobs/med_rep.html')

@app.route('/jobs/nurse', methods=['GET'])
def nurse():
    return render_template('jobs/nurse.html')

@app.route('/jobs/paramed', methods=['GET'])
def paramed():
    return render_template('jobs/paramed.html')

@app.route('/jobs/pharma', methods=['GET'])
def pharma():
    return render_template('jobs/pharma.html')

@app.route('/jobs/physio', methods=['GET'])
def physio():
    return render_template('jobs/physio.html')

@app.route('/jobs/radio', methods=['GET'])
def radio():
    return render_template('jobs/radio.html')



# OTP Email Sending Function
def send_email(recipient_email, otp,username):
    with app.app_context():  # Create the application context
        msg = Message('Your OTP for MedJobHub', sender="MedJobHub <medjobhub>", recipients=[recipient_email])
        msg.body = f"""
Hello {username},
Thank you for using our services. To complete your verification, please use the following One-Time Password (OTP):
{otp}
This OTP is valid for 10 minutes and is intended to secure your account and identity. Please do not share this code with anyone.
If you did not request this OTP, please ignore this message or contact our support team immediately.

Best regards,
MEJoBHUb
"""
        try:
            mail.send(msg)
            print("Email sent successfully!")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
        
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Get the form data
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists
        user = User.query.filter_by(username=username).first()
        if user:
            # Check if the password is correct
            if check_password_hash(user.password, password):
                if not user.is_verified:
                    # Generate OTP for unverified user
                    otp = random.randint(100000, 999999)
                    otp_storage[username] = otp
                    print(f"Generated OTP for {username}: {otp}")  # Debugging purposes
                    if send_email(user.email, otp, username):
                        flash('OTP has been sent to your email.', 'info')
                        return redirect(url_for('verify_otp', username=username))
                    else:
                        flash('Error sending OTP. Please try again later.', 'error')
                        return redirect(url_for('signin'))
                else:
                    # Set the session for verified user
                    session['user_id'] = user.id
                    flash('You are successfully logged in.', 'success')
                    return redirect(url_for('home'))
            else:
                flash('Incorrect password. Please try again.', 'error')
        else:
            flash('Username not found. Please check your username.', 'error')

    return render_template('signin.html')



@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    username = request.args.get('username')
    if request.method == 'POST':
        username = request.form.get('username')
        entered_otp = request.form['otp']
        stored_otp = otp_storage.get(username)

        if stored_otp and int(entered_otp) == stored_otp:
            user = User.query.filter_by(username=username).first()
            if user:
                session['user_id'] = user.id
                user.is_verified = True
                db.session.commit()
                otp_storage.pop(username, None)  # Clear OTP after successful verification
                flash('OTP verified successfully! You are now logged in.', 'success')
                return redirect(url_for('home'))
        flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html', username=username)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first', 'warning')
        return redirect(url_for('signin'))

    # Get the username from the session and retrieve the corresponding user
    user_id = session['user_id']  # Assuming you store user_id in session
    user = User.query.filter_by(id=user_id).first()

    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('signin'))

    # Fetch user's profile details (additional user details)
    user_profile = user.additional_details  # Assuming relationship is set correctly

    # Handle profile form submission (if POST)
    if request.method == 'POST':
        # If profile doesn't exist, create it
        if not user_profile:
            user_profile = UserProfile(user_id=user.id)
            db.session.add(user_profile)

        # Save form data to the database
        user_profile.skills = request.form.get('skills', '').strip()
        user_profile.education = request.form.get('education', '').strip()
        user_profile.work_experience = request.form.get('work_experience', '').strip()
        user_profile.certifications = request.form.get('certifications', '').strip()

        try:
            # Commit the changes to the database
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))  # Avoid re-submission on refresh
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving profile: {e}', 'error')

    # Render profile page with the user's data (persisted even after logout)
    return render_template('profile.html', user=user, user_profile=user_profile)


@app.route('/profile/get_data', methods=['GET'])
def get_profile_data():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # Fetch user profile data
    user_profile = user.additional_details  # Assuming additional_details stores the user's saved data

    # Construct the data to return
    profile_data = {
        'social_links': {
            'website': user_profile.website if user_profile else '',
            'github': user_profile.github if user_profile else '',
            'twitter': user_profile.twitter if user_profile else '',
            'instagram': user_profile.instagram if user_profile else '',
            'facebook': user_profile.facebook if user_profile else ''
        },
        'education_text': user_profile.education if user_profile else '',
        'skills': user_profile.skills if user_profile else '',
        'work_experience': user_profile.work_experience if user_profile else '',
        'certifications': user_profile.certifications if user_profile else ''
    }

    return jsonify({'success': True, 'data': profile_data})




@app.route('/signup', methods=['GET', 'POST'])
def signup():
    session.pop('user_id', None)
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        gender = request.form.get('gender')
        age = request.form.get('age')
        address=request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate password match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('signup'))

        # Check for existing user
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create new user instance
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            phone=phone,
            email=email,
            gender=gender,
            age=age,
            address=address,
            password=hashed_password
        )

        # Add and commit the new user
        db.session.add(new_user)
        db.session.commit()

        # Generate and store OTP
        otp = random.randint(100000, 999999)
        otp_storage[username] = otp
        print(f"Generated OTP for {username}: {otp}")  # Simulate sending OTP via email/SMS

        # Flash success message and redirect to signin
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('signin'))

    return render_template('signup.html')

    




@app.route('/medabout')
def medabout():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/profile/save_social_links', methods=['POST'])
def save_social_links():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404

    # Function to normalize URLs by ensuring they contain http:// or https://
    def normalize_url(url):
        if not url:
            return None
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return "http://" + url  # Default to http:// if no protocol is provided

    if user:
        data = request.get_json()
        social_links = data.get('links')  # Extract social links from the "links" field

        # Normalize the URLs before saving
        social_links['website'] = normalize_url(social_links.get('website'))
        social_links['github'] = normalize_url(social_links.get('github'))
        social_links['twitter'] = normalize_url(social_links.get('twitter'))
        social_links['instagram'] = normalize_url(social_links.get('instagram'))
        social_links['facebook'] = normalize_url(social_links.get('facebook'))

        # Fetch or create the UserProfile for the current user
        user_profile = UserProfile.query.filter_by(user_id=user.id).first()
        if not user_profile:
            # Create a new UserProfile if it doesn't exist
            user_profile = UserProfile(user_id=user.id)
            db.session.add(user_profile)

        # Update social media links in the UserProfile model
        user_profile.website = social_links.get('website')
        user_profile.github = social_links.get('github')
        user_profile.twitter = social_links.get('twitter')
        user_profile.instagram = social_links.get('instagram')
        user_profile.facebook = social_links.get('facebook')

        # Commit changes to the database
        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Links saved successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error saving social links: {str(e)}'})
    else:
        return jsonify({'success': False, 'message': 'User not found'})



@app.route('/profile/save_skills', methods=['POST'])
def save_skills():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'result': 'User not logged in'}), 401

    # Get the username from the session and retrieve the corresponding user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'result': 'User not found'}), 404

    # Get the skills data from the request
    data = request.get_json()
    skills = data.get('data')

    print('Received skills:', skills)  # Debugging

    if not skills:
        return jsonify({'result': 'No skills provided'}), 400

    if not user.additional_details:
        user_profile = UserProfile(user_id=user.id)
        db.session.add(user_profile)
    else:
        user_profile = user.additional_details

    # Update skills in the profile
    user_profile.skills = skills

    # Commit the changes to the database
    try:
        db.session.commit()
        print('Skills saved successfully')  # Debugging
        return jsonify({'result': 'Skills saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print('Error saving skills:', e)  # Debugging
        return jsonify({'result': 'Error saving skills', 'error': str(e)}), 500




@app.route('/profile/get_skills', methods=['GET'])
def get_skills():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'data': ''}), 200

    # Get the username from the session and retrieve the corresponding user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'data': ''}), 200

    # Retrieve the skills from the user's profile
    if user.additional_details:
        skills = user.additional_details.skills
        return jsonify({'data': skills}), 200
    else:
        return jsonify({'data': ''}), 200

@app.route('/profile/save_education', methods=['POST'])
def save_education():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first', 'warning')
        return redirect(url_for('signin'))

    # Get the username from the session and retrieve the corresponding user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('signin'))

    # Get the education data from the request
    data = request.get_json()
    education = data.get('data')

    if not education:
        return jsonify({'result': 'No education details provided'}), 400

    # Check if the user has a profile
    if not user.additional_details:
        user_profile = UserProfile(user_id=user.id)
        db.session.add(user_profile)
    else:
        user_profile = user.additional_details

    # Update education in the profile
    user_profile.education = education

    # Commit the changes to the database
    try:
        db.session.commit()
        return jsonify({'result': 'Education saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'result': 'Error saving education', 'error': str(e)}), 500


@app.route('/profile/get_education', methods=['GET'])
def get_education():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'data': ''}), 200

    # Get the username from the session and retrieve the corresponding user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'data': ''}), 200

    # Retrieve the education details from the user's profile
    if user.additional_details:
        education = user.additional_details.education
        return jsonify({'data': education}), 200
    else:
        return jsonify({'data': ''}), 200

@app.route('/profile/save_workexperience', methods=['POST'])
def save_work_experience():
    if 'user_id' not in session:
        return jsonify({'result': 'User not logged in'}), 401

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'result': 'User not found'}), 404

    data = request.get_json()
    work_experience = data.get('data')

    if not work_experience:
        return jsonify({'result': 'No work experience provided'}), 400

    if not user.additional_details:
        user_profile = UserProfile(user_id=user.id)
        db.session.add(user_profile)
    else:
        user_profile = user.additional_details

    user_profile.work_experience = work_experience

    try:
        db.session.commit()
        return jsonify({'result': 'Work experience saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'result': 'Error saving work experience', 'error': str(e)}), 500



@app.route('/profile/get_work_experience', methods=['GET'])
def get_work_experience():
    if 'user_id' not in session:
        return jsonify({'data': ''}), 200

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404


    if not user:
        return jsonify({'data': ''}), 200

    if user.additional_details:
        work_experience = user.additional_details.work_experience
        return jsonify({'data': work_experience}), 200
    else:
        return jsonify({'data': ''}), 200
    

    


# Helper function to check allowed file types
def allowed_file(filename):
    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/profile/upload_education', methods=['POST'])
def upload_education():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Get the current user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404

    # Retrieve uploaded file and text
    education_file = request.files.get('education_file')
    education_text = request.form.get('education_text')

    # Check if both file and text are missing
    if not education_file and not education_text:
        return jsonify({'error': 'No education details provided'}), 400

    # Handle file upload if provided
    file_path = None
    filename = None
    if education_file and allowed_file(education_file.filename):
        filename = secure_filename(education_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        education_file.save(file_path)

    # Retrieve or create user profile
    user_profile = user.additional_details if user.additional_details else UserProfile(user_id=user.id)
    db.session.add(user_profile)

    # Update the profile with file path, filename, and text (if provided)
    if file_path:
        user_profile.education_file = file_path  # Save file path in the dedicated field
    if filename:
        user_profile.education_filename = filename  # Save the filename (optional but helpful)
    if education_text:
        user_profile.education = education_text  # Save the education text

    try:
        db.session.commit()
        return jsonify({'success': 'Education details saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving education details: {str(e)}'}), 500


@app.route('/profile/upload_certifications', methods=['POST'])
def upload_certifications():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Get the current user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Retrieve certifications text
    certifications_text = request.form.get('certifications_text')

    # Check if certifications text is provided
    if not certifications_text:
        return jsonify({'error': 'No certifications text provided'}), 400

    # Retrieve or create user profile
    user_profile = user.additional_details if user.additional_details else UserProfile(user_id=user.id)
    db.session.add(user_profile)

    # Save certifications text to the profile
    user_profile.certifications = certifications_text  # Save text in the database

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Certifications text saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error saving certifications text: {str(e)}'}), 500


@app.route('/uploads/<filename>')
def serve_file(filename):
    # Serve files from the upload folder
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/profile/save_certificates', methods=['POST'])
def save_certificates():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    # Get the current user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({'result': 'User not found'}), 404

    app.logger.debug(f"Fetched user with ID: {user.id}")

    # Retrieve uploaded file and text
    certificate_file = request.files.get('certificate_file')
    certificate_text = request.form.get('certificate_text')

    # Debug the received values
    app.logger.debug(f"Received certificate_text: {certificate_text}")
    if certificate_file:
        app.logger.debug(f"Received file: {certificate_file.filename}")
    else:
        app.logger.debug("No certificate file uploaded.")

    # Check if both file and text are missing
    if not certificate_file and not certificate_text:
        return jsonify({'error': 'No certificate details provided'}), 400

    # Handle file upload if provided
    file_path = None
    if certificate_file and allowed_file(certificate_file.filename):
        filename = secure_filename(certificate_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        certificate_file.save(file_path)
        app.logger.debug(f"Certificate file saved to: {file_path}")
    else:
        app.logger.debug("No file uploaded or invalid file format.")

    # Retrieve or create user profile
    if not user.additional_details:
        app.logger.debug(f"Creating new user profile for user {user.id}")
        user_profile = UserProfile(user_id=user.id)
        db.session.add(user_profile)
    else:
        user_profile = user.additional_details
        app.logger.debug(f"Found existing user profile for user {user.id}")

    # Update the profile with file path and text (if provided)
    if file_path:
        user_profile.certificates_file = file_path  # Save file path in a dedicated field
        app.logger.debug(f"Updated certificate file path in profile: {user_profile.certificates_file}")

    if certificate_text:
        user_profile.certificates_text = certificate_text  # Ensure this assignment is correct
    try:
        db.session.commit()
        app.logger.info(f"Certificate details saved successfully for user {user.id}")
        return jsonify({'success': 'Certificate details saved successfully'}), 200
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error saving certificate details for user {user.id}: {str(e)}")
        return jsonify({'error': f'Error saving certificate details: {str(e)}'}), 500



@app.route('/profile/get_certifications', methods=['GET'])
def get_certifications():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'data': ''}), 200

    # Get the username from the session and retrieve the corresponding user
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'result': 'User not logged in'}), 401

    user = User.query.get(user_id)
    

    # Retrieve the certifications from the user's profile
    if user.additional_details:
        certifications = user.additional_details.certifications
        return jsonify({'data': certifications}), 200
    else:
        return jsonify({'data': ''}), 200

@app.route('/logout')
def logout():
    # Clear the session
    session.pop('user_id', None)  # Remove the user from the session

    # Flash a message for successful logout
    flash('You have been logged out successfully.', 'success')

    # Redirect the user to the home page or login page
    return redirect(url_for('home'))


from io import BytesIO
from flask import send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    # Simulate a logged-in user (replace with session or authentication logic)
    user_id = session.get('user_id') # Example user ID

    # Fetch the user from the database
    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Return the user_id as JSON
    return jsonify({
        "success": True,
        "user_id": user.id,
        "username": user.username  # Optionally include other details
    })

from flask import Flask, request, session, jsonify, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import traceback
import re

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    try:
        # Retrieve user ID from session
        app.logger.info("Attempting to retrieve user_id from session")
        user_id = session.get('user_id')
        app.logger.info(f"User ID from session: {user_id}")

        # Check if user is logged in
        if not user_id:
            app.logger.warning("User not logged in, session expired or invalid")
            return jsonify({"error": "Unauthorized access. Please log in first."}), 401

        # Retrieve user and user profile data from the database
        app.logger.info("Fetching user from the database")
        user = User.query.get(user_id)
        if not user:
            app.logger.warning(f"User with ID {user_id} not found in the database")
            return jsonify({"error": "User not found."}), 404

        app.logger.info(f"Fetching profile details for user: {user_id}")
        user_profile = user.additional_details  # Accessing the related UserProfile
        if not user_profile:
            app.logger.warning(f"User profile for user {user_id} not found.")
            return jsonify({"error": "User profile data not found."}), 404

        # Check profile fields for missing data
        app.logger.info("Checking profile fields for missing data")
        if not user_profile.education:
            app.logger.warning("Education not provided")
        if not user_profile.work_experience:
            app.logger.warning("Work experience not provided")
        if not user_profile.certifications:
            app.logger.warning("Certifications not provided")
        if not user_profile.skills:
            app.logger.warning("Skills not provided")

        # Create a PDF in memory
        app.logger.info("Starting PDF creation process")
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Add Header: Name and Contact Information
        elements.append(Paragraph(f"<b>{user.first_name} {user.last_name}</b>", styles['Title']))
        contact_info = (
            f"<b>Email:</b> {user.email or 'Not provided'} | "
            f"<b>Phone:</b> {user.phone or 'Not provided'} | "
            f"<b>Address:</b> {user.address or 'Not provided'}"
        )
        elements.append(Paragraph(contact_info, styles['Normal']))
        elements.append(Spacer(1, 24))

        # Education Section
        elements.append(Paragraph("<b>Education</b>", styles['Heading2']))
        education = user_profile.education.strip() if user_profile.education else "Not provided"
        elements.append(Paragraph(education, styles['Normal']))
        elements.append(Spacer(1, 24))

        # Experience Section
        elements.append(Paragraph("<b>Experience</b>", styles['Heading2']))
        experience = user_profile.work_experience.strip() if user_profile.work_experience else "Not provided"
        elements.append(Paragraph(experience, styles['Normal']))
        elements.append(Spacer(1, 24))

        # Certifications Section
        elements.append(Paragraph("<b>Certifications</b>", styles['Heading2']))
        certifications = user_profile.certifications.strip() if user_profile.certifications else "Not provided"
        elements.append(Paragraph(certifications, styles['Normal']))
        elements.append(Spacer(1, 24))

        # Skills Section
        elements.append(Paragraph("<b>Skills</b>", styles['Heading2']))
        if user_profile.skills:
            skills = [skill.strip() for skill in user_profile.skills.split(",") if skill.strip()]
            if skills:
                skills_table = Table([[skill] for skill in skills], colWidths=[400])
                skills_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ]))
                elements.append(skills_table)
            else:
                elements.append(Paragraph("No skills provided.", styles['Normal']))
        else:
            elements.append(Paragraph("No skills provided.", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Social Links Section
        elements.append(Paragraph("<b>Social Links</b>", styles['Heading2']))
        social_links = [
            ("Website", user_profile.website),
            ("GitHub", user_profile.github),
            ("Twitter", user_profile.twitter),
            ("Instagram", user_profile.instagram),
            ("Facebook", user_profile.facebook),
        ]
        for label, link in social_links:
            if link:
                if re.match(r'^(http|https)://', link.strip()):
                    elements.append(Paragraph(f"<b>{label}:</b> <a href='{link.strip()}' target='_blank'>{link.strip()}</a>", styles['Normal']))
                else:
                    elements.append(Paragraph(f"<b>{label}:</b> Invalid URL", styles['Normal']))
            else:
                elements.append(Paragraph(f"<b>{label}:</b> Not provided", styles['Normal']))
        elements.append(Spacer(1, 24))

        # Build the PDF
        app.logger.info("Building the PDF")
        pdf.build(elements)
        buffer.seek(0)

        # Return the generated PDF for download
        app.logger.info("PDF generated successfully")
        response = send_file(
            buffer,
            as_attachment=True,
            download_name="generated_resume.pdf",
            mimetype='application/pdf'
        )
        return response

    except Exception as e:
        # Log the exception with full traceback
        app.logger.error(f"Exception occurred: {str(e)}")
        app.logger.error("Traceback: " + traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred while generating the resume."}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
        
        # Reset verification status for all users
        users = User.query.all()
        for user in users:
            user.is_verified = False
        db.session.commit()

    app.run(debug=True)