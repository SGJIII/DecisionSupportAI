from flask import request, render_template
from . import index_blueprint
from utils.epic_data import fetch_patient_data, get_epic_token

@index_blueprint.route('/fetch-patient-data', methods=['POST'])
def fetch_patient_data_view():
    api_key = request.form['api_key']
    patient_id = request.form['patient_id']
    # Store API key in session or a secure place
    # Fetch patient data
    token = get_epic_token(api_key)  # Modify get_epic_token to accept API key if needed
    patient_data = fetch_patient_data(token, patient_id)
    return render_template('patient_data.html', data=patient_data)
