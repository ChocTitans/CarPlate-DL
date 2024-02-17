from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# config.py
app = Flask(__name__)
app.secret_key = "yoursecretkey"
DATABASE_URL = 'postgresql://pfadb:serveurs..00@pfadb.postgres.database.azure.com:5432/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)