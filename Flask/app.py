from flask import Flask, render_template, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
from models import User, Person, PoliceBrigader, PoliceTonSite, Vehicle, FichierDeRecherche
from flask import Flask, request
from config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

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
        session_db.close()

        if user:
            return render_template('liste-fiche.html')
    return render_template('index.html')

@app.route('/add-fiche-button')
def addfichebutton():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        session_db = Session()
        user = session_db.query(User).filter_by(email=email, password=password).first()

        if user:
            # Store user information in the session
            session['user_id'] = user.id
            return redirect(url_for('location'))  # Redirect to dashboard or any other page after login
        else:
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

@app.route('/video')
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

@app.route('/upload_video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        if 'user_id' in session:  # Check if user is logged in
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            video = request.files['video']
            video_path = f"uploads/{video.filename}"  # Define the path to save the uploaded video
            video.save(video_path)

            return "Video uploaded and processed successfully"  # Or redirect to a result page

        else:
            return redirect(url_for('index'))  # Redirect to index/login page if user is not logged in

    return render_template('upload.html')  # Render the upload form

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

        # Create a new FichierDeRecherche instance
        new_fiche = FichierDeRecherche(name=nom_fiche, address=last_seen_address, description=description)

        # Fetch the Person and Vehicle based on selected IDs
        with Session() as session_db:
            selected_person = session_db.query(Person).filter_by(cin=selected_person_id).first()
            selected_vehicle = session_db.query(Vehicle).filter_by(car_plate=selected_vehicle_id).first()

            # Associate Person and Vehicle with the new FichierDeRecherche
            if selected_person:
                new_fiche.person = selected_person
            if selected_vehicle:
                new_fiche.vehicle = selected_vehicle

            # Add the new FichierDeRecherche to the session and commit changes
            session_db.add(new_fiche)
            session_db.commit()

        # Redirect to a success page or return a success message
        return "Form submitted successfully!"

    # Handle other HTTP methods or errors here
    return "Invalid request method"