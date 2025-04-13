from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from model_ai import predict_pneumonia
import os
from extension import db
from flask import send_file
import io


app = Flask(__name__)
app.secret_key = 'secret-key'
app.config.from_object('config.Config')
db.init_app(app)

from models import User, Patient, Image

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['role'] = user.role
        session['nom'] = user.nom
        if user.role == 'admin':
            return redirect(url_for('dashboard_admin'))
        else:
            return redirect(url_for('dashboard_med'))
    return render_template('login.html', erreur="Identifiants incorrects")

@app.route('/dashboard_admin')
def dashboard_admin():
    if session.get('role') != 'admin':
        return redirect('/')
    medecins = User.query.filter_by(role='medecin').all()
    return render_template('dashboard_admin.html', medecins=medecins)

@app.route('/ajouter_medecin', methods=['POST'])
def ajouter_medecin():
    nom = request.form['nom']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    if User.query.filter_by(email=email).first():
        return "Email déjà utilisé."
    medecin = User(nom=nom, email=email, password=password, role='medecin')
    db.session.add(medecin)
    db.session.commit()
    return redirect(url_for('dashboard_admin'))

@app.route('/supprimer_medecin/<int:id>')
def supprimer_medecin(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('dashboard_admin'))

@app.route('/dashboard_med')
def dashboard_med():
    if session.get('role') != 'medecin':
        return redirect('/')
    return render_template('dashboard_med.html')

@app.route('/patients')
def patients():
    if session.get('role') != 'medecin':
        return redirect('/')

    # Récupérer les patients du médecin connecté
    patients = Patient.query.filter_by(medecin_id=session['user_id']).all()
    return render_template('patients.html', patients=patients)


@app.route('/image/<int:patient_id>')
def afficher_image(patient_id):
    image = Image.query.filter_by(patient_id=patient_id).first()
    if image:
        return send_file(io.BytesIO(image.data), mimetype='image/jpeg')
    return "Image non trouvée"

@app.route('/ajouter_patient', methods=['POST'])
def ajouter_patient():
    nom = request.form['nom']
    age = request.form['age']
    ville = request.form['ville']
    sexe = request.form['sexe']
    description = request.form['description']
    patient = Patient(nom=nom, age=age, ville=ville, sexe=sexe,
                      description=description, medecin_id=session['user_id'])
    db.session.add(patient)
    db.session.commit()
    return redirect(url_for('upload_image', patient_id=patient.id))

@app.route('/upload/<int:patient_id>')
def upload_image(patient_id):
    return render_template('upload.html', patient_id=patient_id)

@app.route('/predict/<int:patient_id>', methods=['POST'])
def predict(patient_id):
    file = request.files['image']
    if file.filename == '':
        return "Aucun fichier sélectionné."

    # Enregistrer l'image temporairement
    path = os.path.join('uploads', file.filename)
    file.save(path)

    # Sauvegarder une copie dans /static/preview.jpg pour affichage
    static_preview = os.path.join('static', 'preview.jpg')
    file.seek(0)  # repositionne le curseur au début du fichier
    with open(static_preview, 'wb') as f:
        f.write(file.read())

    # Prédiction AI
    resultat, confiance = predict_pneumonia(path)

    # Sauvegarder l'image et les résultats en base
    file.seek(0)
    image = Image(data=file.read(), resultat=resultat, confiance=confiance, patient_id=patient_id)
    db.session.add(image)
    db.session.commit()

    # Afficher les résultats
    return render_template('result.html', resultat=resultat, confiance=confiance)

@app.route('/logout')
def logout():
    session.clear()  # supprime toutes les données de session
    return redirect(url_for('home'))  # redirige vers la page de connexion


if __name__ == '__main__':
    app.run(debug=True)
