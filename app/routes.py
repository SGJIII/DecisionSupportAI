# app/routes.py
from flask import Flask, request, redirect, url_for, render_template, jsonify
from fhir.fhir_client import FhirClient

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/oauth-callback')
def oauth_callback():
    code = request.args.get('code')
    fhir_client = FhirClient()
    fhir_client.authenticate(code)
    # Redirect to the patient ID entry page
    return redirect(url_for('index'))

@app.route('/handle-patient-id', methods=['POST'])
def handle_patient_id():
    data = request.get_json()
    patient_id = data['patientId']
    # Add logic to handle patient ID (e.g., fetching patient data using FHIR client)
    # ...
    # For demonstration, returning a simple JSON response
    return jsonify({'message': f'Patient ID {patient_id} received and processed'})

# Add additional routes as needed

if __name__ == "__main__":
    app.run(debug=True)


