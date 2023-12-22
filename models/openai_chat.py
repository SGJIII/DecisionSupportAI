import requests
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def query_openai(text):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-4-1106-preview',
        'messages': [
            {'role': 'system', 'content': 'You are a virtual assistant trained to provide clinical decision support. While you are not a doctor, you can offer insights based on medical data and research. Please assess any articles given as additional context.'},
            {'role': 'user', 'content': text}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error in OpenAI API call: {response.text}")

if __name__ == "__main__":
    sample_text = "Please provide a detailed clinical decision or recommendation for a patient with the following symptoms: [symptoms]."
    try:
        result = query_openai(sample_text)
        print(result)
    except Exception as e:
        print(f"Failed to get response from OpenAI: {e}")
