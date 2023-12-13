from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)
    type = Column(String)  # This column helps determine the type of user

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, email, password):
        self.email = email 
        self.password = password

class PoliceBrigader(User):
    __tablename__ = 'police_brigaders'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    badge_number = Column(Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'police_brigader',
    }

    def __init__(self, email, password, badge_number):
        super().__init__(email, password)
        self.badge_number = badge_number

class PoliceTonSite(User):
    __tablename__ = 'police_ton_sites'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    site_code = Column(String)
    
    __mapper_args__ = {
        'polymorphic_identity': 'police_ton_site',
    }

    def __init__(self, email, password, site_code):
        super().__init__(email, password)
        self.site_code = site_code


class Person(Base):
    __tablename__ = 'persons'
    cin = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(Date)
    address = Column(String)

    fichiers = relationship("FichierDeRecherche", back_populates="person")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    car_plate = Column(String, primary_key=True)
    model = Column(String)

    fichiers = relationship("FichierDeRecherche", back_populates="vehicle")

class FichierDeRecherche(Base):
    __tablename__ = 'fichiers_de_recherche'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    description = Column(String)
    person_cin = Column(String, ForeignKey('persons.cin'))
    vehicle_car_plate = Column(String, ForeignKey('vehicles.car_plate'))

    person = relationship("Person", back_populates="fichiers")
    vehicle = relationship("Vehicle", back_populates="fichiers")