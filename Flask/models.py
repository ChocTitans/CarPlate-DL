from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from config import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import DateTime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    type = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, email, password):
        self.email = email
        self.password = password

class PoliceTerrain(User):
    __tablename__ = 'police_ton_sites'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    badge_number = db.Column(db.String)

    location_history = db.relationship("LocationHistory", back_populates="police_ton_site")

    __mapper_args__ = {
        'polymorphic_identity': 'police_ton_site',
    }

    def __init__(self, email, password, badge_number, first_name=None, last_name=None):
        super().__init__(email, password)
        self.badge_number = badge_number
        self.first_name = first_name
        self.last_name = last_name

class PoliceBrigader(User):
    __tablename__ = 'police_brigaders'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    badge_number = db.Column(db.String)

    __mapper_args__ = {
        'polymorphic_identity': 'police_brigader',
    }

    def __init__(self, email, password, badge_number, first_name=None, last_name=None):
        super().__init__(email, password)
        self.badge_number = badge_number
        self.first_name = first_name
        self.last_name = last_name
        
class LocationHistory(db.Model):
    __tablename__ = 'location_history'
    id = db.Column(db.Integer, primary_key=True)
    police_ton_site_id = db.Column(db.Integer, db.ForeignKey('police_ton_sites.id'))
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    street_name = db.Column(db.String)  # New column for street name
    recorded_at = db.Column(DateTime, default=datetime.utcnow)  # Column for recording time

    police_ton_site = db.relationship("PoliceTerrain", back_populates="location_history")

    def __init__(self, police_ton_site_id, latitude, longitude, street_name, recorded_at):
        self.police_ton_site_id = police_ton_site_id
        self.latitude = latitude
        self.longitude = longitude
        self.street_name = street_name
        self.recorded_at = recorded_at

class Person(db.Model):
    __tablename__ = 'persons'
    cin = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    dob = db.Column(db.Date)
    address = db.Column(db.String)

    fichiers = db.relationship("FichierDeRecherche", back_populates="person")

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    car_plate = db.Column(db.String)
    model = db.Column(db.String)
    Status = db.Column(db.String)

    fichiers = db.relationship("FichierDeRecherche", back_populates="vehicle")
    historic_entries = db.relationship("HistoricVoiture", back_populates="vehicle")

class HistoricVoiture(db.Model):
    __tablename__ = 'historic_voitures'
    id = db.Column(Integer, primary_key=True)
    vehicle_id = db.Column(String, ForeignKey('vehicles.id'))
    recorded_at = db.Column(DateTime, default=datetime.utcnow)  # New column for recording time
    localisation = db.Column(String)

    vehicle = db.relationship("Vehicle", back_populates="historic_entries")

class FichierDeRecherche(db.Model):
    __tablename__ = 'fichiers_de_recherche'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    description = db.Column(db.String)
    person_cin = db.Column(db.String, db.ForeignKey('persons.cin'))
    vehicle_car_plate = db.Column(db.String, db.ForeignKey('vehicles.car_plate'))

    person = db.relationship("Person", back_populates="fichiers")
    vehicle = db.relationship("Vehicle", back_populates="fichiers")


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_progress = db.Column(db.Integer, default=0)