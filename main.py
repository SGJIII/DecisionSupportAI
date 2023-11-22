import csv
from models.llama_chat import query_llama_with_retry
from utils.data_processing import load_emr_data
from utils.pubmed_fetch import fetch_pubmed_data, fetch_article_details

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


def main():
    emr_data = load_emr_data("data/mock_emr.csv")
    results = []

    for record in emr_data:
    # Fetch PubMed articles with more details
        article_ids = fetch_pubmed_data(
            diagnosis=record['diagnosis'],
            gender=record['gender'],
            symptoms=record['symptoms'],
            medical_history=record['medical_history'],
            test_results=record['test_results'],
            medications=record['medications'])
        articles = fetch_article_details(article_ids) if article_ids else []

        # Create a prompt for LLaMa with PubMed context
        prompt = create_llama_prompt(record, articles)
        print("Sending prompt to LLaMa:", prompt)  # For debugging

        # Query LLaMa and store the result
        llama_response = query_llama_with_retry(prompt)

        # Extract and print the generated text
        generated_text = llama_response[0]['generated_text']
        print("Generated Text:", generated_text)

    results.append({'patient_id': record['patient_id'], 'llama_response': generated_text})


    # Write results to a CSV file
    with open('data/llama_responses.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['patient_id', 'llama_response'])
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    main()


