import csv
from models.clinical_bert import query_clinicalbert_with_retry
from utils.data_processing import load_emr_data
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details

def create_clinicalbert_prompt(patient_record):
    prompt = (
        f"Age: {patient_record['age']}\n"
        f"Gender: {patient_record['gender']}\n"
        f"Symptoms: {patient_record['symptoms']}\n"
        f"Medical History: {patient_record['medical_history']}\n"
        f"Test Results: {patient_record['test_results']}\n"
        f"Diagnosis: {patient_record['diagnosis']}\n"
        f"Medications: {patient_record['medications']}\n"
        f"Notes: {patient_record['notes']}\n\n"
        f"A detailed clinical decision or recommendation for this patient is [MASK]."
    )
    return prompt


def main():
    emr_data = load_emr_data("data/mock_emr.csv")
    results = []

    for record in emr_data:
        # Fetch PubMed articles based on patient's diagnosis
        article_ids = fetch_pubmed_data(record['diagnosis'])
        articles = fetch_article_details(article_ids) if article_ids else []

        # Create a prompt for ClinicalBERT
        prompt = create_clinicalbert_prompt(record)  # Updated to pass only one argument
        print("Sending prompt to ClinicalBERT:", prompt)  # Add this line for debugging

        # Query ClinicalBERT and store the result
        clinicalbert_response = query_clinicalbert_with_retry(prompt)
        results.append({'patient_id': record['patient_id'], 'clinicalbert_response': clinicalbert_response})

    # Write results to a CSV file
    with open('data/clinicalbert_responses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['patient_id', 'clinicalbert_response'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    main()

