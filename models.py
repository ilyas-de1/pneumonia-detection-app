from extension import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))
    patients = db.relationship('Patient', backref='medecin', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    age = db.Column(db.Integer)
    ville = db.Column(db.String(100))
    sexe = db.Column(db.String(10))
    description = db.Column(db.Text)
    medecin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.relationship('Image', uselist=False, backref='patient')

from datetime import datetime

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary)
    resultat = db.Column(db.String(50))
    confiance = db.Column(db.Float)
    date_analyse = db.Column(db.DateTime, default=datetime.utcnow)  # ✅ nouveau champ
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
