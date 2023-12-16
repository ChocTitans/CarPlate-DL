# init_db.py
from datetime import date


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base, PoliceBrigader, PoliceTonSite,Person, Vehicle
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Create admin user
# Adding a Police Brigader
brigader_email = 'b@b.com'
brigader_password = 'b'
brigader_badge_number = 12345

brigader_user = PoliceBrigader(email=brigader_email, password=brigader_password, badge_number=brigader_badge_number)
session.add(brigader_user)

# Adding a Police Ton Site
ton_site_email = 't@t.com'
ton_site_password = 't'
ton_site_code = 'TON123'

ton_site_user = PoliceTonSite(email=ton_site_email, password=ton_site_password, site_code=ton_site_code)

Personne = Person(cin='AA88520',first_name='Hamza', last_name='Boubnane', dob=date(1990, 1, 1), address='Address Details')

# Add instances to the session and commit to the database
session.add(Personne)
session.add(brigader_user)
session.add(ton_site_user)
session.commit()

print("Database initialized successfully.")
