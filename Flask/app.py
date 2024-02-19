import datetime
from flask import Flask, render_template, request, url_for, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import User, Vehicle, PoliceTerrain, PoliceBrigader, Person, LocationHistory, FichierDeRecherche, HistoricVoiture
from flask import Flask, request
from config import DATABASE_URL, app, db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import logging

dl_app_url='https://flask.hamzaboubnane.tech'
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
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        if user:
            return render_template('location.html')
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            if user.type == 'police_brigader':
                session['user_id'] = user.id
                return redirect(url_for('dashboard'))  # Redirect based on user type (if needed)
            
        return redirect(url_for('index'))  # Redirect if login fails


@app.route('/logout')
def logout():
    # Clear the user_id from the session if it exists
    session.pop('user_id', None)
    
    # Redirect to the index or login page after logout
    return redirect(url_for('index'))


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
        fiches = load_fiche_recherche()
        people = load_people()
        pt = load_police_terrain()

        if user and people:
            total_persons = len(people)
            total_fiches = len(fiches)
            previous_month_total = 1  # Replace this with the actual previous month's total
            percentage_change = ((total_persons - previous_month_total) / previous_month_total) * 100
            percentage_change_fiches = ((total_fiches - previous_month_total) / previous_month_total * 100)

        return render_template('dashboard.html', pt=pt, total_fiches=total_fiches,fiches=fiches, percentage_change_fiches=percentage_change_fiches,total_persons=total_persons, percentage_change=percentage_change)
    
    return redirect(url_for('index'))



######################################################################
#               
#                   FUNCTIONS WITHOUT ROUTING
#
######################################################################

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

def load_fiche_recherche():
    try:
        fiche_recherche_data = FichierDeRecherche.query.all()
        return fiche_recherche_data
    except Exception as e:
        # Handle exceptions if necessary
        logging.error(f'Error loading fiche_recherche: {e}', exc_info=True)
        return None
    
def load_police_terrain():
    try:
        pt_data = PoliceTerrain.query.all()
        return pt_data
    except Exception as e:
        # Handle exceptions if necessary
        logging.error(f'Error loading fiche_recherche: {e}', exc_info=True)
        return None

######################################################################
#               
#                   API REDIRECTIONS TO PT SITE
#
######################################################################

@app.route('/api/update_vehicle_status', methods=['POST'])
def update_vehicle_status():
    data = request.json
    vehicle_id = data.get('vehicle_id')
    new_status = data.get('Status')

    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        vehicle.Status = new_status
        db.session.commit()
        return jsonify({'message': 'Vehicle status updated successfully'}), 201
    else:
        return jsonify({'error': 'Vehicle not found'}), 404 


@app.route('/api/save_vehicle', methods=['POST'])
def save_vehicle():
    data = request.json

    if 'license_plate' not in data or 'user_id' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Create a new vehicle instance
    new_vehicle = Vehicle(
        car_plate=data['license_plate'],
        model='Car',  # Set the model as required
        Status='Non Recherche'  # Set the initial status as required
    )

    # Add the vehicle to the database
    db.session.add(new_vehicle)
    db.session.commit()
    print(new_vehicle.id)
    return jsonify({'message': 'Vehicle saved successfully', 'vehicle_id': new_vehicle.id}), 201

    
@app.route('/api/save_vehicle_localisation', methods=['POST'])
def save_vehicle_localisation():
    data = request.json

    # Retrieve data from the JSON payload
    vehicle_id = data.get('vehicle_id')
    localisation = data.get('localisation')
    recorded_at = data.get('recorded_at')

    # Create a new HistoricVoiture entry
    new_localisation = HistoricVoiture(vehicle_id=vehicle_id, localisation=localisation, recorded_at=recorded_at)
    
    # Add and commit to the database
    db.session.add(new_localisation)
    db.session.commit()

    # Send a response back to the client
    response_data = {'message': 'Vehicle localisation saved successfully'}
    return jsonify(response_data), 201
    
@app.route('/api/save_location', methods=['POST'])
def save_location_pb():
    data = request.json
    print(data)
    police_ton_site_id = data.get('police_ton_site_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    street_name = data.get('street_name')
    recorded_at = data.get('recorded_at')

    try:

        # Create a LocationHistoryPB entry
        location_entry_pb = LocationHistory(
            police_ton_site_id=police_ton_site_id,
            latitude=latitude,
            longitude=longitude,
            street_name=street_name,
            recorded_at=recorded_at
        )

        # Save the location entry to the PB database
        db.session.add(location_entry_pb)
        db.session.commit()

        return jsonify({'message': 'Location saved successfully on PB'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

######################################################################
#               
#                   CRUD FOR PERSON
#
######################################################################
@app.route('/edit-person/<string:person_cin>', methods=['GET', 'POST'])
def edit_person(person_cin):
    person = Person.query.get(person_cin)

    if request.method == 'POST':
        person.first_name = request.form['first_name']
        person.last_name = request.form['last_name']
        person.dob = request.form['dob']
        person.address = request.form['address']

        db.session.commit()

        return redirect(url_for('personlist'))  # Update with the correct route for your person list page

    return render_template('edit-person.html', person=person)

@app.route('/add-person', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        cin = request.form['cin']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        address = request.form['address']

        new_person = Person(cin=cin, first_name=first_name, last_name=last_name, dob=dob, address=address)
        db.session.add(new_person)
        db.session.commit()

        return redirect(url_for('personlist'))  # Update with the correct route for your person list page

    return render_template('add-person.html')

@app.route('/add-person-popup', methods=['POST'])
def add_person_popup():
    if request.method == 'POST':
        cin = request.form['person_cin']
        first_name = request.form['person_first_name']
        last_name = request.form['person_last_name']
        dob = request.form['person_dob']
        address = request.form['person_address']

        new_person = Person(cin=cin, first_name=first_name, last_name=last_name, dob=dob, address=address)
        db.session.add(new_person)
        db.session.commit()

        # You can add any additional logic here if needed

    # For simplicity, you can just refresh the current page after submitting the form
    return redirect(request.referrer or url_for('index'))  # Change 'index' to the actual route of your page

# Delete Person
@app.route('/delete-person/<string:person_cin>', methods=['GET','POST'])
def delete_person(person_cin):
    person = Person.query.get(person_cin)

    if person:
        db.session.delete(person)
        db.session.commit()

    return redirect(url_for('personlist'))  # Update with the correct route for your person list page

@app.route('/person-list')
def personlist():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        person = Person.query.all()

        if person or user:
            return render_template('personlist.html', person=person)
    
    return render_template('index.html')

######################################################################
#               
#                   CRUD FOR FIELD COP
#
######################################################################

@app.route('/cop-list')
def coplist():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        cop = PoliceTerrain.query.all()

        if cop or user:
            return render_template('list-terraincop.html', cop=cop)
    
    return render_template('index.html')

@app.route('/delete-cop/<int:officer_id>', methods=['GET', 'POST'])
def delete_cop(officer_id):
    cop = PoliceTerrain.query.get(officer_id)

    if cop:
        db.session.delete(cop)
        db.session.commit()

    return redirect(url_for('coplist'))

@app.route('/edit-cop/<int:officer_id>', methods=['GET', 'POST'])
def edit_cop(officer_id):
    cop = PoliceTerrain.query.get(officer_id)

    if request.method == 'POST':
        cop.first_name = request.form['first_name']
        cop.last_name = request.form['last_name']
        cop.last_name = request.form['last_name']
        cop.email = request.form['email']
        cop.password = request.form['password']
        cop.badge_number = request.form['badge_number']

        db.session.commit()

        return redirect(url_for('coplist'))

    return render_template('edit-terraincop.html', cops=cop)

@app.route('/cop-list/<int:officer_id>', methods=['GET'])
def officer_history(officer_id):
    cop = PoliceTerrain.query.get(officer_id)
    if cop:
        history = cop.location_history
        return render_template('historic-terraincop.html', cop=cop, history=history)
    else:
        # Handle if officer ID doesn't exist
        return render_template('index.html')

@app.route('/add-cop')
def addcop():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()

        if user:
            try:
                return render_template('add-terraincop.html')
            except Exception as e:
                # Handle exceptions if necessary
                logging.error(f'Error fetching data for add-fiche: {e}', exc_info=True)
                return render_template('dashboard.html')
    
    return render_template('index.html')

@app.route('/submit-cop-form', methods=['POST'])
def submit_form_cop():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        badge_number = request.form['badge_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Create a PoliceTerrain instance and add it to the database
        new_police_terrain = PoliceTerrain(email=email, password=password, badge_number=badge_number, first_name=first_name, last_name=last_name)

        db.session.add(new_police_terrain)
        db.session.commit()

        # Redirect or render a success page
        return redirect(url_for('coplist'))

    # Handle other cases or errors
    return render_template('dashboard.html')  # You can replace 'error.html' with your error page
######################################################################
#               
#                   CRUD FOR FICHE DE RECHERCHE
#
######################################################################


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
            selected_vehicle.Status = "Recherche"


        db.session.add(new_fiche)
        db.session.commit()

        return redirect(url_for('ficheliste'))

    return "Invalid request method"
    
@app.route('/delete-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def deletefiche(fichier_id):
    fichier = FichierDeRecherche.query.get(fichier_id)
    if fichier:
        associated_vehicle = fichier.vehicle  # Retrieve associated vehicle
        if associated_vehicle:
            associated_vehicle.Status = "Non Recherche"  # Update Status to "Non Recherche"
        db.session.delete(fichier)
        db.session.commit()
            
    return redirect(url_for('ficheliste'))



@app.route('/edit-fiche/<int:fichier_id>', methods=['GET', 'POST'])
def editfiche(fichier_id):
    fichier = FichierDeRecherche.query.get(fichier_id)
    all_people = Person.query.all()
    all_vehicles = Vehicle.query.all()

    if request.method == 'POST':
        fichier.name = request.form['nom_fiche']
        fichier.address = request.form['address']
        fichier.person_cin = request.form['selectedPerson']
        fichier.vehicle_car_plate = request.form['selectedVehicle']
        fichier.description = request.form['description']

        db.session.commit()

        return redirect(url_for('ficheliste'))

    return render_template('edit-fiche.html', fichier=fichier, all_people=all_people, all_vehicles=all_vehicles)

######################################################################
#               
#                   CRUD FOR VEHICLES
#
######################################################################

@app.route('/add-vehicle-popup', methods=['POST'])
def add_vehicle_popup():
    if request.method == 'POST':
        car_plate = request.form['car_plate']
        model = request.form['model']

        new_vehicle = Vehicle(car_plate=car_plate, model=model, Status='Recherche')
        db.session.add(new_vehicle)
        db.session.commit()

        # You can add any additional logic here if needed

    # For simplicity, you can just refresh the current page after submitting the form
    return redirect(request.referrer or url_for('index'))  # Change 'index' to the actual route of your page


@app.route('/vehicule-liste')
def vehiculeliste():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.filter_by(id=user_id).first()
        vehicles = load_vehicles()

        if vehicles or user:
            return render_template('liste-vehicules.html', vehicles=vehicles)
    
    return render_template('index.html')

@app.route('/delete-vehicle/<int:vehicle_id>', methods=['GET', 'POST'])
def deletevehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle:
        db.session.delete(vehicle)
        db.session.commit()
        
    return redirect(url_for('vehiculeliste'))


@app.route('/car-historic/<int:car_id>')
def car_historic(car_id):
    car = Vehicle.query.get(car_id)
    if car:
        historic_entries = car.historic_entries
        return render_template('historic-vehicules.html', historic_entries=historic_entries)
    # Handle case if the car ID doesn't exist
    return "Car ID not found"




@app.route('/api/vehicles', methods=['GET'])
def get_updated_vehicles():
    try:
        # Fetch updated vehicle information from the database
        vehicles = load_vehicles()

        # Prepare the vehicle data to be sent in JSON format
        vehicle_data = [
            {
                'type': vehicle.model,
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
        