# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Create admin user
admin_email = 'admin@admin.com'
admin_password = 'admin'
admin_user = User(email=admin_email, password=admin_password)
session.add(admin_user)
session.commit()

print("Database initialized successfully.")
