from flask import Flask, render_template, request, url_for, session, redirect, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import current_app
from DL.models import User, Vehicle, PoliceTerrain, PoliceBrigader, Person, LocationHistory, FichierDeRecherche, HistoricVoiture, Progress
from DL.config import DATABASE_URL, db, app
import os
import subprocess
from datetime import datetime
import json
from sqlalchemy.orm import aliased
from sqlalchemy import desc
import requests
import certifi
import logging

API_URL= 'https://flask.hamzaboubnane.tech'
UPLOAD_FOLDER = 'uploads'
people_data = None
vehicles_data = None
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


######################################################################
#               
#                   ROUTING IN GENERAL
#
######################################################################

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
                police_ton_site = session_db.query(PoliceTerrain).filter_by(id=user.id).first()
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
    session.pop('user_id', None)
    return redirect(url_for('index'))
   
@app.route('/location')
def location():
    if 'user_id' in session:
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('location.html')
    else:
        return redirect(url_for('index'))

@app.route('/save-location', methods=['POST'])
def save_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # Call Google Geocoding API to convert latitude and longitude to a street address
    api_key = 'AIzaSyBtX8iuhcojHtbqT7FXCAiTCRm32TGXX9c'
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'OK':

            results = result['results']
            if results:
                first_result = results[1]
                street_name = first_result['formatted_address']       
            police_ton_site_id = session.get('police_ton_site_id')
            
            if police_ton_site_id:
                recorded_time = datetime.utcnow().replace(second=0, microsecond=0)  # Get current UTC time without seconds and microseconds
                location_entry = LocationHistory(police_ton_site_id=police_ton_site_id, latitude=latitude, longitude=longitude, street_name=street_name, recorded_at=recorded_time)
                # Add and commit the entry using SQLAlchemy session
                db.session.add(location_entry)
                db.session.commit()
                
                return {'success': True}
            else:
                return {'success': False}
        else:
            return {'success': False}
    else:
        return {'success': False}
    

@app.route('/run_detection', methods=['POST'])
def run_detection():
    if request.method == 'POST':
        video_filename = request.form['video_filename']  # Get the video filename
        
        # Assuming user_id is available in the session
        user_id = session.get('user_id')
        if user_id:
            subprocess.Popen(['python', './carplate/main.py', video_filename, str(user_id)])
            return 'Detection process started!'
        else:
            return 'User ID not found in session'
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
    if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            if user.type == 'police_ton_site':
                police_ton_site = PoliceTerrain.query.get(user_id)
                location_history = LocationHistory.query.filter_by(police_ton_site_id=police_ton_site.id).order_by(desc(LocationHistory.id)).first()
                
    vehicles = Vehicle.query.all()
    return render_template('upload.html', vehicles=vehicles, location_history=location_history)


######################################################################
#               
#                   FUNCTIONS WITHOUT ROUTING
#
######################################################################
    

def save_license_plate(license_plate_text, user_id):
    with current_app.app_context():
        user = User.query.get(user_id)
        if user.type == 'police_ton_site':
            police_ton_site = PoliceTerrain.query.get(user_id)
            if police_ton_site:
                latest_location = (
                    LocationHistory.query
                    .filter_by(police_ton_site_id=police_ton_site.id)
                    .order_by(LocationHistory.recorded_at.desc())
                    .first()
                )
                recorded_at = datetime.utcnow().replace(second=0, microsecond=0)
                localisation = latest_location.street_name if latest_location else None

                # Check if the license plate exists in FicherdeRecherche
                existing_vehicule = Vehicle.query.filter_by(car_plate=license_plate_text).first()

                if existing_vehicule:
                    existing_record = FichierDeRecherche.query.filter_by(vehicle_car_plate=license_plate_text).first()
                    
                    if existing_record:
                        existing_vehicule.Status = "Recherche"
                        #db.session.commit()
                    else:
                        # Check if the vehicle already has a record in the same street area
                        existing_location = (
                            HistoricVoiture.query
                            .filter_by(
                                vehicle=existing_vehicule,
                                localisation=localisation  # Assuming street_name is the street area field
                            )
                            .first()
                        )
                        print(existing_location)
                        if existing_location:
                            # Print the vehicle's existing location for comparison
                            print("no")
                        if not existing_location:
                            # Add the location history for the vehicle
                            historic_entry = HistoricVoiture(vehicle=existing_vehicule, localisation=localisation, recorded_at=recorded_at)
                            #db.session.add(historic_entry)
                            #db.session.commit()

                else:
                    # Add the license plate if it doesn't exist
                    new_vehicle = Vehicle(car_plate=license_plate_text, model='Voiture', Status="Non Recherche")
                    #db.session.add(new_vehicle)
                    #db.session.commit()

                    historic_entry = HistoricVoiture(vehicle=new_vehicle, localisation=localisation, recorded_at=recorded_at)
                    #db.session.add(historic_entry)
                    #db.session.commit()
        api_data = {
            'license_plate': license_plate_text,
            'user_id': user_id,
            'recorded_at': recorded_at.isoformat(),
            'localisation': localisation,
            'historic_entry': {
                'id': historic_entry.id,
                'vehicle_id': historic_entry.vehicle_id,
                'localisation': historic_entry.localisation,
                'recorded_at': historic_entry.recorded_at.isoformat()
            } if historic_entry else None
        }


        # Send data to PB API
        pb_api_url = f'{API_URL}/api/save_vehicle'
        requests.post(pb_api_url, json=api_data, verify=False)

def video():
    if 'user_id' in session:
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('upload.html')
    else:
        return redirect(url_for('index'))

######################################################################
#               
#                   API PROGRESS FOR VIDEO LOADING BAR
#
######################################################################

@app.route('/reset_progress')
def reset_progress():
    progress_entry = Progress.query.first()
    if progress_entry:
        progress_entry.current_progress = 0
        db.session.commit()
        return jsonify({'message': 'Progress reset to 0 successfully.'}), 200
    return jsonify({'message': 'No progress entry found.'}), 404

@app.route('/update_progress/<int:progress>', methods=['GET'])
def update_progress(progress):
    progress_entry = Progress.query.first()
    if not progress_entry:
        progress_entry = Progress(current_progress=progress)
        db.session.add(progress_entry)
    else:
        progress_entry.current_progress = progress

    db.session.commit()
    return jsonify({'message': 'Progress updated successfully.'})

@app.route('/get_progress', methods=['GET'])
def get_progress():
    progress_entry = Progress.query.first()
    if progress_entry:
        return jsonify({'progress': progress_entry.current_progress})
    return jsonify({'progress': 0})

@app.route('/api/updated_vehicles', methods=['GET'])
def updated_vehicles():

    dl_updated_vehicles_endpoint = f'{API_URL}/api/vehicles'

    try:
        response = requests.get(dl_updated_vehicles_endpoint, verify=False)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Failed to fetch updated vehicles from external API. Status Code: {response.status_code}'}), 500
    except requests.RequestException as e:
        logging.error(f'Request Exception: {e}', exc_info=True)
        return jsonify({'error': f'Request Exception: {e}'}), 500

@app.route('/apis/updated_vehicles')
def updateds_vehicles():
    vehicles = Vehicle.query.all()
    vehicle_data = [
        {
            'car_plate': vehicle.car_plate,
            'Status': vehicle.Status,
            'index': vehicle.id
        }
        for vehicle in vehicles
    ]

    return jsonify(vehicle_data)