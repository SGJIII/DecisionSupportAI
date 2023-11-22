import requests
import time

def query_llama(text):
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
    headers = {"Authorization": "Bearer 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"}
    payload = {"inputs": text}

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error response from LLaMa:", response.text)  # Print error response
        raise Exception(f"Error in LLaMa API call: {response.status_code}")

def query_llama_with_retry(text):
    if not isinstance(text, str):
        raise ValueError("Text must be a string")

    for attempt in range(5):
        try:
            response = requests.post(
                'https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf',
                headers={'Authorization': f'Bearer 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'},
                json={'inputs': text}
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error response from LLaMa: {response.text}")
                print(f"Attempt {attempt + 1}/5 failed: Error in LLaMa API call: {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt + 1}/5 failed: {str(e)}")
            time.sleep(1)
    raise Exception("Failed to get a valid response from LLaMa after 5 attempts")



# Example usage
if __name__ == "__main__":
    sample_text = "Please provide a detailed clinical decision or recommendation for a patient with the following symptoms: [symptoms]."
    try:
        result = query_llama_with_retry(sample_text)
        print(result)
    except Exception as e:
        print(f"Failed to get response from LLaMa: {e}")
