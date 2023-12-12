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


person_fichier_association = Table('person_fichier_association', Base.metadata,
    Column('person_id', Integer, ForeignKey('persons.id')),
    Column('fichier_id', Integer, ForeignKey('fichiers_de_recherche.id'))
)

# Define association table for Vehicle and FichierDeRecherche
vehicle_fichier_association = Table('vehicle_fichier_association', Base.metadata,
    Column('vehicle_id', Integer, ForeignKey('vehicles.id')),
    Column('fichier_id', Integer, ForeignKey('fichiers_de_recherche.id'))
)

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    dob = Column(Date)
    address = Column(String)
    # Other attributes of a person

    fichiers = relationship("FichierDeRecherche", secondary=person_fichier_association, back_populates="persons")

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    model = Column(String)
    car_plate = Column(String)
    # Other attributes of a vehicle

    fichiers = relationship("FichierDeRecherche", secondary=vehicle_fichier_association, back_populates="vehicles")
class FichierDeRecherche(Base):
    __tablename__ = 'fichiers_de_recherche'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Other attributes of a search file

    persons = relationship("Person", secondary=person_fichier_association, back_populates="fichiers")
    vehicles = relationship("Vehicle", secondary=vehicle_fichier_association, back_populates="fichiers")