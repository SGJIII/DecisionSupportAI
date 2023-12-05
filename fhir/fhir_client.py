# fhir/fhir_client.py
import requests
from flask import current_app

class FhirClient:
    def __init__(self):
        self.base_url = current_app.config['EPIC_FHIR_BASE_URL']
        self.token = None

    def authenticate(self, code):
        token_url = current_app.config['EPIC_TOKEN_ENDPOINT']
        data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['REDIRECT_URI'],
        'client_id': current_app.config['EPIC_CLIENT_ID'],
        'client_secret': current_app.config['EPIC_CLIENT_SECRET']
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            self.token = response.json()['access_token']
        else:
            raise Exception("Failed to obtain access token")

    def get_patient_data(self, patient_id):
        if not self.token:
            raise Exception("Authentication required")

        headers = {'Authorization': f'Bearer {self.token}'}
        patient_url = f"{self.base_url}/Patient/{patient_id}"
        response = requests.get(patient_url, headers=headers)

        if response.status_code == 200:
            patient_data = response.json()
            # Example extraction logic (adjust based on actual API response structure)
            extracted_data = {
                'age': patient_data.get('age'),  # Adjust field names as per the API response
                'gender': patient_data.get('gender'),
                'symptoms': patient_data.get('symptoms'),
                'medical_history': patient_data.get('medicalHistory'),
                'test_results': patient_data.get('testResults'),
                'diagnosis': patient_data.get('diagnosis'),
                'medications': patient_data.get('medications')
            }
            return extracted_data
        else:
            raise Exception("Failed to retrieve patient data")




