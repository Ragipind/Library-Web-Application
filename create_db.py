from app import app
from extensions import db  # or from app import db if db is defined in app.py

with app.app_context():
    db.create_all()
    print(" Database created successfully.")
