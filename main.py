import csv
import uuid
import os
from flask import Flask, request, redirect, render_template, jsonify, url_for
from models.llama_chat import query_llama_with_retry
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details
from auth.oauth_handler import get_auth_url, exchange_code_for_token
from fhir.fhir_client import FhirClient
from config import EPIC_CLIENT_ID_PROD
import config

# Define the base directory of your application
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask app with the new template folder path
app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'app/static/templates'),
            static_folder=os.path.join(basedir, 'app/static'))

# Load configuration from config.py
app.config.from_object('config')

def create_llama_prompt(patient_record, articles):
    prompt = (
        f"Given a {patient_record['age']}-year-old {patient_record['gender']} with {patient_record['symptoms']} "
        f"and diagnosed with {patient_record['diagnosis']}, what would be your recommendation?\n\n"
    )

    if articles:
        prompt += "Here are some articles and abstracts for additional context to help with your recommendation:\n\n"
        for article in articles:
            prompt += f"Title: {article['title']}\nAbstract: {article['abstract']}\n\n"

    return prompt

def process_patient_record(record):
    articles = fetch_articles_for_record(record)
    prompt = create_llama_prompt(record, articles)
    llama_response = query_llama_with_retry(prompt)
    generated_text = llama_response[0]['generated_text']

    return {'patient_id': record['patient_id'], 'llama_response': generated_text}

def fetch_articles_for_record(record):
    article_ids = fetch_pubmed_data(
        diagnosis=record['diagnosis'],
        gender=record['gender'],
        symptoms=record['symptoms'],
        medical_history=record['medical_history'],
        test_results=record['test_results'],
        medications=record['medications'])
    return fetch_article_details(article_ids) if article_ids else []

def generate_unique_state():
    return str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_auth')
def start_auth():
    state = generate_unique_state()
    auth_url = get_auth_url(state)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    # Add state validation logic here if necessary
    token_info = exchange_code_for_token(code)
    # Store the access token in a session or a secure place
    # Redirect to the patient ID entry page
    return redirect(url_for('index'))

@app.route('/handle-patient-id', methods=['POST'])
def handle_patient_id():
    data = request.get_json()
    patient_id = data['patientId']
    # Assuming you have a way to retrieve the access token stored earlier
    access_token = 'your_access_token'  # Replace with actual token retrieval logic
    fhir_client = FhirClient()
    fhir_client.token = access_token
    patient_data = fhir_client.get_patient_data(patient_id)
    results = [process_patient_record(patient_data)]

    with open('data/llama_responses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['patient_id', 'llama_response'])
        writer.writeheader()
        writer.writerows(results)
    
    return jsonify({'message': 'Patient data processed successfully'})

if __name__ == "__main__":
    app.run(debug=True)
