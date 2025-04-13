from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Charger le modèle entraîné (assure-toi que ce chemin est correct)
model = load_model('models/model_pneumonie.h5')

def predict_pneumonia(img_path):
    """
    Prédit si une radiographie montre une pneumonie.
    Retourne :
        - Le diagnostic ('PNEUMONIE' ou 'NORMAL')
        - Le pourcentage de confiance (float)
    """
    # Chargement et prétraitement de l'image
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalisation

    # Prédiction
    prediction = model.predict(img_array)[0][0]
    confidence = float(prediction) * 100

    # Interprétation
    if prediction > 0.5:
        return "PNEUMONIE", round(confidence, 2)
    else:
        return "NORMAL", round(100 - confidence, 2)
