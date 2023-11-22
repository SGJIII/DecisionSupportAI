import requests
import time

def query_clinicalbert(text):
    API_URL = "https://api-inference.huggingface.co/models/medicalai/ClinicalBERT"
    headers = {"Authorization": "Bearer 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"}
    payload = {"inputs": text}

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error response from ClinicalBERT:", response.text)  # Print error response
        raise Exception(f"Error in ClinicalBERT API call: {response.status_code}")

def query_clinicalbert_with_retry(text, max_retries=5):
    for i in range(max_retries):
        try:
            return query_clinicalbert(text)
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise e

# Example usage
if __name__ == "__main__":
    sample_text = "The patient shows symptoms of [MASK]."
    try:
        result = query_clinicalbert_with_retry(sample_text)
        print(result)
    except Exception as e:
        print(f"Failed to get response from ClinicalBERT: {e}")


