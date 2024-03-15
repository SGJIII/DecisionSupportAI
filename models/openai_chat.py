import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def query_openai(text):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        #'model': 'gpt-4-1106-preview', #gpt 4 hight end. very expensive
        'model': 'gpt-3.5-turbo-16k-0613', #gpt 3.5 turbo order of magnitide cheaper. Use for testing non response features. 
        'messages': [
            {'role': 'system', 'content': 'You are a virtual assistant trained to provide clinical decision support. While you are not a doctor, you can offer insights based on medical data and research. Please assess any articles given as additional context. Please never speak in the first person.'},
            {'role': 'user', 'content': text}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error in OpenAI API call: {response.text}")
    
def summarize_patient_data(symptoms, patient_data):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }
    patient_data_str = json.dumps(patient_data)  # Convert patient data to a string
    data = {
        'model': 'gpt-4-1106-preview',  # Updated to use gpt-3.5-turbo model
        'messages': [
            {'role': 'system', 'content': 'Your job is to summarize the given patient data based on the symptoms. Please only return a summary of the data that you have been given. It is important not to add anything that is not in the patient data but also not to leave anything important out. Please never speak in the first person.'},
            {'role': 'user', 'content': f"Patient data: {patient_data_str}\nSymptoms: {symptoms}\n\Please summarize the parts of the Patient data that are relevant to the symptom(s) provided. Please let me know which pieces are specifically relevant to the symptoms and which may not be but might be important. Please be very precise and extremely detailed with your response including any specific lab results and test dates, and relevant encounter dates etc. that might be relevant to the symptoms provided. It's important to know when relevant labs were taken and encounters happened. Please present this in a concise and structured format for easy reading e.g. bullet points."}
        ]
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=headers)  # Updated endpoint
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']  # Updated to correctly parse the response
    else:
        raise Exception(f"Error in OpenAI API call: {response.text}")

if __name__ == "__main__":
    sample_text = "Please provide a detailed clinical decision or recommendation for a patient with the following symptoms: [symptoms]."
    try:
        result = query_openai(sample_text)
        print(result)
    except Exception as e:
        print(f"Failed to get response from OpenAI: {e}")
