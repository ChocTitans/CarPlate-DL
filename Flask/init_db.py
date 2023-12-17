from datetime import date
from models import User, PoliceBrigader, PoliceTonSite, Person, Vehicle, Progress
from config import db, app

# This line will create all the tables based on the models
with app.app_context():
    db.create_all()

    # Create admin user
    brigader_email = 'b@b.com'
    brigader_password = 'b'
    brigader_badge_number = 12345

    brigader_user = PoliceBrigader(email=brigader_email, password=brigader_password, badge_number=brigader_badge_number)
    db.session.add(brigader_user)

    ton_site_email = 't@t.com'
    ton_site_password = 't'
    ton_site_code = 'TON123'

    ton_site_user = PoliceTonSite(email=ton_site_email, password=ton_site_password, site_code=ton_site_code)

    person = Person(cin='AA88520', first_name='Hamza', last_name='Boubnane', dob=date(1990, 1, 1), address='Address Details')

    db.session.add(person)
    db.session.add(ton_site_user)

    # Adding Progress
    initial_progress = Progress(current_progress=0)
    db.session.add(initial_progress)

    # Commit changes to the database
    db.session.commit()

    print("Database initialized successfully.")
