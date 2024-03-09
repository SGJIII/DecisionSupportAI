from fhir.fhir_client import FHIRClient
from flask import current_app

def fetch_patient_data(access_token, patient_id):
    fhir_client = FHIRClient(current_app.config['EPIC_FHIR_URL'], access_token)
    return fhir_client.get_patient(patient_id)

