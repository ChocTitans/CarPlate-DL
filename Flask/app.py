from flask import Flask, render_template, request, url_for, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import User, Person, PoliceBrigader, PoliceTonSite, Vehicle, FichierDeRecherche, LocationHistory
from flask import Flask, request
from config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests

app = Flask(__name__)
app.secret_key = "yoursecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
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
    global people_data
    if people_data is None:
        session_db = Session()
        people_data = session_db.query(Person).all()
        session_db.close()
    return people_data

def load_vehicles():
    global vehicles_data
    if vehicles_data is None:
        session_db = Session()
        vehicles_data = session_db.query(Vehicle).all()
        session_db.close()
    return vehicles_data

@app.route('/add-fiche')
def addfiche():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()

        if user:
            # Fetch data for dropdowns
            people = load_people()
            vehicles = load_vehicles()
            return render_template('add-fiche.html', people=people, vehicles=vehicles)
    
    return render_template('index.html')


@app.route('/fiche-liste')
def ficheliste():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        fichiers = session_db.query(FichierDeRecherche).all()

        if fichiers or user:
            return render_template('liste-fiche.html', fichiers=fichiers)
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

@app.route('/location', methods=['GET'])
def location():
    dl_app_url = 'http://localhost:5050'
    dl_location_endpoint = f'{dl_app_url}/location'

    requests.get(dl_location_endpoint)
    return redirect(dl_location_endpoint)

        
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
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('dashboard.html')
    else:
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

        with Session() as session_db:
            selected_person = session_db.query(Person).filter_by(cin=selected_person_id).first()
            selected_vehicle = session_db.query(Vehicle).filter_by(car_plate=selected_vehicle_id).first()

            if selected_person:
                new_fiche.person = selected_person
            if selected_vehicle:
                new_fiche.vehicle = selected_vehicle

            session_db.add(new_fiche)
            session_db.commit()

        return redirect(url_for('ficheliste'))

    return "Invalid request method"
    
@app.route('/delete-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def deletefiche(fichier_id):
    session_db = Session()
    fichier = session_db.query(FichierDeRecherche).get(fichier_id)
    if fichier:
        session_db.delete(fichier)
        session_db.commit()
    return redirect(url_for('ficheliste'))


@app.route('/edit-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def editfiche(fichier_id):
    session_db = Session()
    fichier = session_db.query(FichierDeRecherche).get(fichier_id)

    if request.method == 'POST':
        fichier.name = request.form['nom_fiche']
        fichier.address = request.form['address']
        fichier.person_cin = request.form['selectedPerson']
        fichier.vehicle_car_plate = request.form['selectedVehicle']
        fichier.description = request.form['description']

        session_db.commit()

        return redirect(url_for('ficheliste'))

    return render_template('edit-fiche.html', fichier=fichier)
