from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# config.py
app = Flask(__name__)
app.secret_key = "yoursecretkey"
DATABASE_URL = 'sqlite:///database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)