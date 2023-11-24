import requests
from flask import current_app

def fetch_patient_data(access_token, patient_id):
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f"{current_app.config['EPIC_FHIR_URL']}/Patient/{patient_id}"
    response = requests.get(url, headers=headers)
    return response.json()
