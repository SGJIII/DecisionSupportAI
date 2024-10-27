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
from supabase import create_client, Client

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

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    current_app.logger.debug(f"Clinical Decision Support OpenAI Prompt: {prompt}")
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

    prompt = f"{medical_info}{article_context}\nBased on this information, please provide clinical decision support on how I might treat this patient. Only provide standard procedures if there are no articles. If there are only provide support and suggestions that use the latest science. Note: I understand you're not a doctor."

    return prompt

def generate_unique_state():
    return str(uuid.uuid4())

@app.route('/')
def landing_page():
    return render_template('landing_page.html')

@app.route('/clinical-decision-support')
def clinical_decision_support():
    if not is_authenticated():
        return redirect(url_for('start_auth'))
    return render_template('index.html')

@app.route('/lab-compilation')
def lab_compilation():
    return render_template('lab_compilation.html')

@app.route('/medical-history-summary')
def medical_history_summary():
    if not is_authenticated():
        return redirect(url_for('start_auth'))
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
    return redirect(url_for('medical_history_summary'))  # Change this line

@app.route('/handle-fhir-id', methods=['POST'])
def handle_fhir_id():
    if not is_authenticated():
        return jsonify({'error': 'User not authenticated'}), 401

    data = request.get_json()
    mrn = data.get('mrn')  # Assuming you're sending MRN in your request
    symptoms = data.get('symptoms', '')  # This is new, to receive symptoms from the frontend.
    if not mrn:
        return jsonify({'error': 'MRN is missing'}), 400
    feature = data.get('feature')  # Extract the feature identifier

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

        if feature == "Research Assistant":
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
            # Log the symptoms and the patient_data being sent for summarization
            current_app.logger.debug(f"Medical History Summary Symptoms: {symptoms}")
            current_app.logger.debug(f"Medical History Summary Patient Data: {patient_data}")
            
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

@app.route('/sign_up')
def sign_up():
    return render_template('referral_code.html')

@app.route('/validate_referral_code', methods=['POST'])
def validate_referral_code():
    referral_code = request.form.get('referral_code')
    valid_codes = ['BETA123', 'TESTCODE']  # Replace with actual codes or a database query

    if referral_code in valid_codes:
        session['referral_verified'] = True
        return redirect(url_for('select_hospital'))
    else:
        return render_template('referral_code.html', error='Invalid referral code')

@app.route('/select_hospital')
def select_hospital():
    if not session.get('referral_verified'):
        return redirect(url_for('sign_up'))
    
    # Load hospitals and endpoints
    hospitals = load_hospital_list()
    return render_template('select_hospital.html', hospitals=hospitals)

def load_hospital_list():
    hospitals = []
    with open('hospital_endpoints.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hospitals.append({'name': row['Organization Name'], 'endpoint': row['Production FHIR Base URL - R4']})
    return hospitals

@app.route('/set_hospital_endpoint', methods=['POST'])
def set_hospital_endpoint():
    hospital_endpoint = request.form.get('hospital_endpoint')
    hospital_name = request.form.get('hospital_name')
    if hospital_endpoint and hospital_name:
        session['hospital_endpoint'] = hospital_endpoint
        session['hospital_name'] = hospital_name
        return redirect(url_for('start_auth'))
    else:
        return redirect(url_for('select_hospital'))

@app.route('/login')
def login():
    epic_user_id = session.get('epic_user_id')
    if epic_user_id:
        # Fetch user from Supabase
        response = supabase.table('users').select('*').eq('epic_user_id', epic_user_id).execute()
        if response.data:
            user = response.data[0]
            hospital_endpoint = user.get('hospital_endpoint')
            if hospital_endpoint:
                session['hospital_endpoint'] = hospital_endpoint
                return redirect(url_for('start_auth'))
    # If no user info, redirect to select hospital
    return redirect(url_for('select_hospital'))

@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    if not code:
        return 'Authorization code not found', 400

    # Exchange code for token
    try:
        token_data = exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        epic_user_id = token_data.get('patient')  # Epic user ID
        if not epic_user_id:
            return 'Epic user ID not found in token response', 400

        # Fetch or create user in Supabase
        response = supabase.table('users').select('*').eq('epic_user_id', epic_user_id).execute()
        if response.data:
            user = response.data[0]
            # Update hospital info if necessary
            hospital_name = session.get('hospital_name', user.get('hospital_name'))
            hospital_endpoint = session.get('hospital_endpoint', user.get('hospital_endpoint'))

            supabase.table('users').update({
                'hospital_name': hospital_name,
                'hospital_endpoint': hospital_endpoint
            }).eq('epic_user_id', epic_user_id).execute()
        else:
            # Get hospital info from session
            hospital_name = session.get('hospital_name')
            hospital_endpoint = session.get('hospital_endpoint')

            # Insert new user
            supabase.table('users').insert({
                'epic_user_id': epic_user_id,
                'hospital_name': hospital_name,
                'hospital_endpoint': hospital_endpoint
            }).execute()

        # Store user ID in session
        session['epic_user_id'] = epic_user_id
        session['access_token'] = access_token

        # Proceed with the rest of your logic
        return redirect(url_for('index'))

    except Exception as e:
        app.logger.error(f"OAuth callback error: {e}")
        return 'Authentication failed', 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=8080)
