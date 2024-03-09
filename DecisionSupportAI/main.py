import csv
import uuid
import os
from flask import Flask, request, redirect, render_template, jsonify, url_for, session
from models.llama_chat import query_llama_with_retry
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details
from auth.oauth_handler import get_auth_url, exchange_code_for_token, generate_code_verifier, generate_code_challenge
from fhir.fhir_client import FhirClient
import config
from dotenv import load_dotenv
from flask import current_app
from models.openai_chat import query_openai, summarize_patient_data
import logging_config
from flask import send_from_directory
import traceback

load_dotenv()

logging_config.setup_logging()

# Define the base directory of your application
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app with the new template folder path
app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'app/static/templates'),
            static_folder=os.path.join(basedir, 'app/static'))

# Load configuration from config.py
app.config.from_object('config')

# Set secret key for session
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

def is_authenticated():
    """Check if the user is authenticated."""
    return 'access_token' in session and session['access_token'] is not None


def process_patient_record(patient_data):
    # Fetch articles from PubMed
    article_ids = fetch_pubmed_data(
        age=patient_data.get('age', ''),
        gender=patient_data.get('gender', ''),
        medications=patient_data.get('medications', ''),
        allergies=patient_data.get('allergies', ''),
        conditions=patient_data.get('conditions', ''),
        social_history=patient_data.get('social_history', '')
    )
    articles = fetch_article_details(article_ids) if article_ids else []

    # Create prompt for OpenAI
    prompt = create_openai_prompt(patient_data, articles)
    openai_response = query_openai(prompt)
    generated_text = openai_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    current_app.logger.debug(f"OpenAI Response: {openai_response}")

    return {'patient_data': patient_data, 'prompt': prompt, 'articles': articles, 'openai_response': generated_text}

def create_openai_prompt(patient_data, articles):
    medical_info = f"Patient Information: Age {patient_data['age']}, Gender {patient_data['gender']}, " \
                   f"Medications: {patient_data['medications']}, Allergies: {patient_data['allergies']}, " \
                   f"Conditions: {patient_data['conditions']}, Social History: {patient_data['social_history']}.\n\n"

    article_context = "Here are some relevant PubMed articles for context:\n"
    for article in articles:
        article_context += f"Title: {article['title']}\nAbstract: {article['abstract']}\n"

    prompt = f"{medical_info}{article_context}\nBased on this information, please provide clinical decision support on how I might treat this patient. Note: I understand you're not a doctor."

    return prompt

def generate_unique_state():
    return str(uuid.uuid4())

@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('start_auth'))
    return render_template('index.html')

@app.route('/lab-compilation')
def lab_compilation():
    return render_template('lab_compilation.html')

@app.route('/medical-history-summary')
def medical_history_summary():
    return render_template('medical_history_summary.html')

@app.route('/start_auth')
def start_auth():
    state = generate_unique_state()
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    session['oauth_state'] = state  # Store state in session
    session['code_verifier'] = code_verifier  # Store code_verifier in session
    auth_url = get_auth_url(state, code_challenge)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return 'State mismatch error', 400
    code_verifier = session.get('code_verifier')  # Retrieve code_verifier from session
    token_info = exchange_code_for_token(code, code_verifier)
    session['access_token'] = token_info['access_token']  # Store access token in session
    return redirect(url_for('index'))

@app.route('/handle-fhir-id', methods=['POST'])
def handle_fhir_id():
    if not is_authenticated():
        return jsonify({'error': 'User not authenticated'}), 401

    data = request.get_json()
    mrn = data.get('mrn')  # Assuming you're sending MRN in your request
    symptoms = data.get('symptoms', '')  # This is new, to receive symptoms from the frontend.
    if not mrn:
        return jsonify({'error': 'MRN is missing'}), 400

    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Access token is missing'}), 401

    fhir_client = FhirClient()
    fhir_client.token = access_token

    try:
        # Retrieve FHIR ID from MRN
        fhir_id = fhir_client.get_fhir_id(mrn)
        if not fhir_id:
            return jsonify({'error': 'No FHIR ID found for given MRN'}), 404
        # Retrieve patient data and additional information
        patient_data = fhir_client.get_patient_data_by_fhir_id(fhir_id)

        # Retrieve and process clinical notes
        decoded_clinical_notes = fhir_client.get_all_clinical_notes_content(fhir_id)
        patient_data['clinical_notes'] = decoded_clinical_notes

        # Log the clinical notes for debugging
        current_app.logger.debug("Decoded Clinical Notes:")
        for note in decoded_clinical_notes:
            current_app.logger.debug(note)

        patient_data['medications'] = fhir_client.get_medication_data(fhir_id)
        patient_data['allergies'] = fhir_client.get_allergy_data(fhir_id)
        patient_data['conditions'] = fhir_client.get_condition_data(fhir_id)
        patient_data['social_history'] = fhir_client.get_social_history_data(fhir_id)

              # Fetch and process laboratory observations
        observations_data = fhir_client.fetch_patient_observations(fhir_id, mrn)
        patient_data['laboratory_observations'] = observations_data  # Add observations data to patient data

        # Log the observations for debugging
        current_app.logger.debug("Laboratory Observations Data:")
        current_app.logger.debug(observations_data)

        # Call the method to update the CSV
        fhir_client.update_lab_data_csv(observations_data)  

        procedures_data = fhir_client.fetch_patient_procedures(fhir_id)
        patient_data['procedures'] = procedures_data  # Add procedures data to patient data

        # Log the procedures for debugging
        current_app.logger.debug("Patient Procedures Data:")
        current_app.logger.debug(procedures_data)

        appointments_data = fhir_client.fetch_patient_appointments(fhir_id)
        patient_data['appointments'] = appointments_data  # Add appointments data to patient data

        # Log the appointments for debugging
        current_app.logger.debug("Patient Appointments Data:")
        current_app.logger.debug(appointments_data)

        diagnostic_reports_data = fhir_client.fetch_patient_diagnostic_reports(fhir_id)
        patient_data['diagnostic_reports'] = diagnostic_reports_data  # Add diagnostic reports data to patient data

        # Log the diagnostic reports for debugging
        current_app.logger.debug("Patient Diagnostic Reports Data:")
        current_app.logger.debug(diagnostic_reports_data)

        if symptoms:
            # Assume summarize_patient_data is correctly implemented to handle symptoms and patient_data.
            summary = summarize_patient_data(symptoms, patient_data)
            
            # Construct result to include both summary and patient data.
            result = {
                'summary': summary,
                'patient_data': patient_data  # Ensure this structure aligns with your frontend expectations.
            }
            return jsonify(result)

                # Process patient record
        result = process_patient_record(patient_data)

        # Save or handle the result as needed
        with open('data/llama_responses.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['patient_data', 'prompt', 'openai_response', 'articles'])
            writer.writeheader()
            writer.writerow(result)

        return jsonify(result)  # Return the result as JSON
    except Exception as e:
        current_app.logger.error(f"Error in handle_fhir_id: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-all-lab-data', methods=['GET'])
def get_all_lab_data():
    lab_data = []
    with open('data/Labs/lab_data.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        lab_data = list(reader)
    return jsonify(lab_data)

@app.route('/download-lab-data')
def download_lab_data():
    return send_from_directory('data/Labs', 'lab_data.csv', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=8080)