from app import app
from extension import db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@mail.com').first():
        admin = User(
            nom='Admin',
            email='admin@mail.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✔️ Admin ajouté avec succès.")
    else:
        print("ℹ️ Admin existe déjà.")
