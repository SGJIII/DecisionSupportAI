# fhir/fhir_client.py
import requests
import xml.etree.ElementTree as ET
from flask import current_app
import datetime  # Import the datetime module

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

        # Extracting patient's birth date and calculating age
        birth_date = root.find('.//fhir:birthDate', ns)
        if birth_date is not None:
            patient_birth_date = birth_date.attrib['value']
            patient_age = self.calculate_age(patient_birth_date)
        else:
            patient_age = "Unknown"

        patient_data = {
            'gender': patient_gender,
            'age': patient_age
        }

        return patient_data

    def calculate_age(self, birth_date_str):
        """Calculate age from birth date string (YYYY-MM-DD)."""
        birth_date = datetime.datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        today = datetime.date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age





