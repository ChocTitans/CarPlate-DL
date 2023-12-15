from flask import Flask, render_template, request, url_for, session, redirect, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app
from DL.models import User, Vehicle, PoliceTonSite, PoliceBrigader, Person, LocationHistory
from DL.config import DATABASE_URL, db, app
import os
import subprocess

UPLOAD_FOLDER = 'uploads'
people_data = None
vehicles_data = None

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('location.html')
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        session_db = Session()
        user = session_db.query(User).filter_by(email=email, password=password).first()

        if user:
            if user.type == 'police_ton_site':
                police_ton_site = session_db.query(PoliceTonSite).filter_by(id=user.id).first()
                if police_ton_site:
                    session['user_id'] = user.id
                    session['police_ton_site_id'] = police_ton_site.id
                    return redirect(url_for('location'))  # Redirect to the desired page after login
            else:
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))  # Redirect based on user type (if needed)
        else:
            return redirect(url_for('index'))  # Redirect if login fails


@app.route('/logout')
def logout():
    # Clear the user_id from the session if it exists
    session.pop('user_id', None)
    
    # Redirect to the index or login page after logout
    return redirect(url_for('index'))
   
@app.route('/location')
def location():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('location.html')
    else:
        return redirect(url_for('index'))

def save_license_plate(license_plate_text):
    with current_app.app_context():
        existing_plate = Vehicle.query.filter_by(car_plate=license_plate_text).first()
        if not existing_plate:
            new_vehicle = Vehicle(car_plate=license_plate_text, model='Voiture')  # Set the model as needed
            db.session.add(new_vehicle)
            db.session.commit()

@app.route('/save-location', methods=['POST'])
def save_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    session_db = Session()
    police_ton_site_id = session.get('police_ton_site_id')

    if police_ton_site_id:
        location_entry = LocationHistory(police_ton_site_id=police_ton_site_id, latitude=latitude, longitude=longitude)
        session_db.add(location_entry)
        session_db.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'User not found'})

def video():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('upload.html')
    else:
        return redirect(url_for('index'))

@app.route('/run_detection', methods=['POST'])
def run_detection():
    if request.method == 'POST':
        video_filename = request.form['video_filename']  # Get the video filename
        subprocess.Popen(['python', './carplate/main.py', video_filename])
        return 'Detection process started!'
    else:
        return 'Method Not Allowed'

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'user_id' in session:  # Check if user is logged in
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            video = request.files['video']
            video_path = f"uploads/{video.filename}"  # Define the path to save the uploaded video
            video.save(video_path)
        else:
            return redirect(url_for('index'))  # Redirect to index/login page if user is not logged in

    return render_template('upload.html')  # Render the upload form
