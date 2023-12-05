# app/routes.py
from flask import request, redirect, url_for
from fhir.fhir_client import FhirClient

@app.route('/oauth-callback')
def oauth_callback():
    code = request.args.get('code')
    fhir_client = FhirClient()
    fhir_client.authenticate(code)
    # Example: Fetch patient data
    patient_data = fhir_client.get_resource('Patient', 'patient_id')
    # Process and display the patient data as needed
    return redirect(url_for('display_patient_data'))
