# reset_db.py

from main import app
from models import db

with app.app_context():
    print("🔁 Dropping all tables...")
    db.drop_all()

    print("✅ Creating tables...")
    db.create_all()

    print("🎉 Database reset complete.")


