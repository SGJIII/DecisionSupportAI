import requests

def query_clinicalbert(text):
    API_URL = "https://api-inference.huggingface.co/models/medicalai/ClinicalBERT"
    headers = {"Authorization": "Bearer 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"}
    payload = {"inputs": text}

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error in ClinicalBERT API call: {response.status_code}")

# Example usage
if __name__ == "__main__":
    sample_text = "The patient shows symptoms of [MASK]."
    result = query_clinicalbert(sample_text)
    print(result)
