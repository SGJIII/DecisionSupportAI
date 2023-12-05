import csv
import uuid
from flask import Flask, request, redirect
from models.llama_chat import query_llama_with_retry
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details
from auth.oauth_handler import get_auth_url, exchange_code_for_token
from fhir.fhir_client import FhirClient  # Assuming this module is properly implemented
from config import EPIC_CLIENT_ID_PROD

app = Flask(__name__)

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
    process_patient_data(token_info['access_token'])
    return "Authentication successful"

def process_patient_data(access_token):
    # Example patient ID, replace with actual logic to retrieve patient ID from the frontend
    patient_id = 'example_patient_id'
    fhir_client = FhirClient()
    fhir_client.token = access_token
    patient_data = fhir_client.get_patient_data(patient_id)
    results = [process_patient_record(patient_data)]

    with open('data/llama_responses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['patient_id', 'llama_response'])
        writer.writeheader()
        writer.writerows(results)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
