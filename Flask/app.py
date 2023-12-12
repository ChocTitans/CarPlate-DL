from flask import Flask, render_template, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
from models import User
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

@app.route('/add-fiche')
def addfiche():
    if 'user_id' in session:
        # Fetch user details using session information
        session_db = Session()
        user_id = session['user_id']
        user = session_db.query(User).filter_by(id=user_id).first()
        session_db.close()

        if user:
            return render_template('add-fiche.html')
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
            return render_template('crud.html')
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

if __name__ == '__main__':
    app.run(debug=True)
