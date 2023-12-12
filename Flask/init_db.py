# init_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base, PoliceBrigader, PoliceTonSite
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Create admin user
# Adding a Police Brigader
brigader_email = 'brigader@example.com'
brigader_password = 'brigaderpass'
brigader_badge_number = 12345

brigader_user = PoliceBrigader(email=brigader_email, password=brigader_password, badge_number=brigader_badge_number)
session.add(brigader_user)

# Adding a Police Ton Site
ton_site_email = 'site@example.com'
ton_site_password = 'sitepass'
ton_site_code = 'TON123'

ton_site_user = PoliceTonSite(email=ton_site_email, password=ton_site_password, site_code=ton_site_code)
session.add(ton_site_user)

session.commit()

print("Database initialized successfully.")
