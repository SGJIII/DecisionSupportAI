# fhir/fhir_client.py
import requests
from flask import current_app

class FhirClient:
    def __init__(self):
        self.base_url = current_app.config['EPIC_FHIR_BASE_URL']
        self.token = None

    def get_patient_data_by_mrn(self, mrn):
        if not self.token:
            raise Exception("Authentication required")

        headers = {'Authorization': f'Bearer {self.token}'}
        # Construct the URL to query the patient data using MRN
        patient_url = f"{self.base_url}Patient/{mrn}"
        response = requests.get(patient_url, headers=headers)

        if response.status_code == 200:
            patient_data = response.json()
            return self.extract_patient_data(patient_data)
        else:
            current_app.logger.error(f"Failed to retrieve patient data: {response.text}")
            raise Exception(f"Failed to retrieve patient data: {response.text}")

    def extract_patient_data(self, patient_data):
        # Implement logic to extract relevant fields from the patient_data
        # This is a placeholder function - adjust as per the actual API response
        # Example: Extracting data from the first entry in the bundle
        if 'entry' in patient_data and len(patient_data['entry']) > 0:
            patient = patient_data['entry'][0]['resource']
            return {
                'birthDate': patient.get('birthDate'),  # Adjust field names as per the API response
                'gender': patient.get('gender')
            }
        else:
            raise Exception("No patient data found in the response")

# Additional methods and logic for FhirClient



