from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)

    def __init__(self, email, password):
        self.email = email 
        self.password = password
    
class Video(Base):
    __tablename__ = 'videos'
    id = Column(Integer, primary_key=True)
    path = Column(String)

    def __init__(self, id, path):
        self.id = id
        self.path = path