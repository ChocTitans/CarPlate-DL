from flask import Flask, render_template, request, url_for, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import User, Vehicle, PoliceTonSite, PoliceBrigader, Person, LocationHistory, FichierDeRecherche, HistoricVoiture
from flask import Flask, request
from config import DATABASE_URL, app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import logging

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

def load_people():
    try:
        people_data = Person.query.all()
        return people_data
    except Exception as e:
        # Handle exceptions if necessary
        logging.error(f'Error loading people: {e}', exc_info=True)
        return None

def load_vehicles():
    try:
        vehicles_data = Vehicle.query.all()
        return vehicles_data
    except Exception as e:
        # Handle exceptions if necessary
        logging.error(f'Error loading vehicles: {e}', exc_info=True)
        return None


@app.route('/add-fiche')
def addfiche():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()

        if user:
            try:
                # Fetch data for dropdowns
                people = load_people()
                vehicles = load_vehicles()
                return render_template('add-fiche.html', people=people, vehicles=vehicles)
            except Exception as e:
                # Handle exceptions if necessary
                logging.error(f'Error fetching data for add-fiche: {e}', exc_info=True)
                return render_template('index.html')
    
    return render_template('index.html')


@app.route('/fiche-liste')
def ficheliste():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        fichiers = FichierDeRecherche.query.all()

        if fichiers or user:
            return render_template('liste-fiche.html', fichiers=fichiers)
    
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if user.type == 'police_ton_site':
                police_ton_site = PoliceTonSite.query.filter_by(id=user.id).first()
                if police_ton_site:
                    session['user_id'] = user.id
                    session['police_ton_site_id'] = police_ton_site.id
                    return redirect(url_for('location'))  # Redirect to the desired page after login
            else:
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))  # Redirect based on user type (if needed)
        
        return redirect(url_for('index'))  # Redirect if login fails


@app.route('/logout')
def logout():
    # Clear the user_id from the session if it exists
    session.pop('user_id', None)
    
    # Redirect to the index or login page after logout
    return redirect(url_for('index'))

@app.route('/api/vehicles', methods=['GET'])
def get_updated_vehicles():
    try:
        # Fetch updated vehicle information from the database
        vehicles = load_vehicles()

        # Prepare the vehicle data to be sent in JSON format
        vehicle_data = [
            {
                'car_plate': vehicle.car_plate,
                'Status': vehicle.Status,
                'index': vehicle.id  # Using vehicle id as an index (you can adjust this)
            }
            for vehicle in vehicles
        ]

        return jsonify(vehicle_data)
    except Exception as e:
        # Log the exception for debugging
        logging.error(f'Error fetching vehicle data: {e}', exc_info=True)
        return jsonify({'error': f'Error fetching vehicle data: {str(e)}'}), 500
        
@app.route('/save-location')
def savelocation():
    dl_app_url = 'http://localhost:5050'
    dl_location_endpoint = f'{dl_app_url}/save-location'

    requests.get(dl_location_endpoint)
    return redirect(dl_location_endpoint)

@app.route('/run_detection')
def rundetection():
    dl_app_url = 'http://localhost:5050'
    dl_location_endpoint = f'{dl_app_url}/run_detection'

    requests.get(dl_location_endpoint)
    return redirect(dl_location_endpoint)

@app.route('/upload_video')
def uploadvideo():
    dl_app_url = 'http://localhost:5050'
    dl_location_endpoint = f'{dl_app_url}/upload_video'

    requests.get(dl_location_endpoint)
    return redirect(dl_location_endpoint)


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

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()

        if user:
            return render_template('dashboard.html')
    
    return redirect(url_for('index'))

## CRUD ADD FICHE

@app.route('/submit-form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        # Retrieve form data
        nom_fiche = request.form['nom_fiche']
        selected_person_id = request.form['selectedPerson']
        selected_vehicle_id = request.form['selectedVehicle']
        last_seen_address = request.form['address']
        description = request.form['description']

        new_fiche = FichierDeRecherche(name=nom_fiche, address=last_seen_address, description=description)

        selected_person = Person.query.filter_by(cin=selected_person_id).first()
        selected_vehicle = Vehicle.query.filter_by(car_plate=selected_vehicle_id).first()

        if selected_person:
            new_fiche.person = selected_person
        if selected_vehicle:
            new_fiche.vehicle = selected_vehicle

        db.session.add(new_fiche)
        db.session.commit()

        return redirect(url_for('ficheliste'))

    return "Invalid request method"
    
@app.route('/delete-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def deletefiche(fichier_id):
    fichier = FichierDeRecherche.query.get(fichier_id)
    if fichier:
        db.session.delete(fichier)
        db.session.commit()
    return redirect(url_for('ficheliste'))


@app.route('/edit-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def editfiche(fichier_id):
    fichier = FichierDeRecherche.query.get(fichier_id)

    if request.method == 'POST':
        fichier.name = request.form['nom_fiche']
        fichier.address = request.form['address']
        fichier.person_cin = request.form['selectedPerson']
        fichier.vehicle_car_plate = request.form['selectedVehicle']
        fichier.description = request.form['description']

        db.session.commit()

        return redirect(url_for('ficheliste'))

    return render_template('edit-fiche.html', fichier=fichier)
