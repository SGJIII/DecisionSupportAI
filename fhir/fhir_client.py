# fhir/fhir_client.py
import requests
import xml.etree.ElementTree as ET
from flask import current_app

class FhirClient:
    def __init__(self):
        self.base_url = current_app.config['EPIC_FHIR_BASE_URL']
        self.token = None

    def get_patient_data_by_fhir_id(self, fhir_id):
        if not self.token:
            raise Exception("Authentication required")

        headers = {'Authorization': f'Bearer {self.token}'}
        patient_url = f"{self.base_url}/Patient/{fhir_id}"
        response = requests.get(patient_url, headers=headers)

        current_app.logger.info(f"API Response: {response.status_code}, {response.text}")

        if response.status_code == 200:
            if 'application/xml' in response.headers.get('Content-Type', ''):
                return self.parse_xml_patient_data(response.text)
            else:
                raise Exception("Unsupported response format")
        else:
            raise Exception(f"Failed to retrieve patient data: {response.text}")

    def parse_xml_patient_data(self, xml_data):
        root = ET.fromstring(xml_data)
        ns = {'fhir': 'http://hl7.org/fhir'}

        # Extracting patient's gender
        gender = root.find('.//fhir:gender', ns)
        patient_gender = gender.attrib['value'] if gender is not None else "Unknown"

        # Extracting patient's birth date
        birth_date = root.find('.//fhir:birthDate', ns)
        patient_birth_date = birth_date.attrib['value'] if birth_date is not None else "Unknown"

        patient_data = {
            'gender': patient_gender,
            'birth_date': patient_birth_date
        }

        return patient_data





