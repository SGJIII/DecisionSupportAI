import csv
from flask import Flask, request, redirect
from models.llama_chat import query_llama_with_retry
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details
from auth.oauth_handler import get_auth_url, exchange_code_for_token
from fhir.fhir_client import get_patient_data  # You need to implement this module
from config import EPIC_CLIENT_ID
import uuid

app = Flask(__name__)

def create_llama_prompt(patient_record, articles):
    # Start with the basic prompt
    prompt = (
        f"Given a {patient_record['age']}-year-old {patient_record['gender']} with {patient_record['symptoms']} "
        f"and diagnosed with {patient_record['diagnosis']}, what would be your recommendation?\n\n"
    )

    # Add an introduction for PubMed articles
    ''''''
    if articles:
        prompt += "Here are some articles and abstracts for additional context to help with your recommendation:\n\n"
        for article in articles:
            prompt += f"Title: {article['title']}\nAbstract: {article['abstract']}\n\n"
    else:
        prompt

    return prompt


def process_patient_record(record):
    articles = fetch_articles_for_record(record)
    prompt = create_llama_prompt(record, articles)
    print("Sending prompt to LLaMa:", prompt)  # For debugging

    llama_response = query_llama_with_retry(prompt)
    generated_text = llama_response[0]['generated_text']
    print("Generated Text:", generated_text)

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

import uuid

def generate_unique_state():
    return str(uuid.uuid4())


@app.route('/start_auth')
def start_auth():
    # Generate a unique state parameter for security
    state = generate_unique_state()  # Implement this function
    auth_url = get_auth_url(state)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    # Validate the state parameter here
    token_info = exchange_code_for_token(code)
    # Use token_info['access_token'] to make authenticated requests
    process_patient_data(token_info['access_token'])
    return "Authentication successful"

def process_patient_data(access_token):
    patient_data = get_patient_data(access_token)  # Implement this function to fetch patient data from Epic's FHIR API
    results = [process_patient_record(record) for record in patient_data]

    # Write results to a CSV file
    with open('data/llama_responses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['patient_id', 'llama_response'])
        writer.writeheader()
        writer.writerows(results)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()