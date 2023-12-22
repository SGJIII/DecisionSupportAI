# fhir/fhir_client.py
import requests
import xml.etree.ElementTree as ET
from flask import current_app
import datetime  # Import the datetime module
import json

class FhirClient:
    def __init__(self):
        self.base_url = current_app.config['EPIC_FHIR_BASE_URL']
        self.token = None

    def get_patient_data_by_fhir_id(self, fhir_id):
        try:
            if not self.token:
                raise Exception("Authentication required")

            patient_data = self.get_basic_patient_data(fhir_id)
            patient_data['medications'] = self.get_medication_data(fhir_id)
            patient_data['allergies'] = self.get_allergy_data(fhir_id)
            patient_data['conditions'] = self.get_condition_data(fhir_id)
            patient_data['social_history'] = self.get_social_history_data(fhir_id)

            return patient_data
        except Exception as e:
            current_app.logger.error(f"Error in get_patient_data_by_fhir_id: {e}")
            raise

    def get_basic_patient_data(self, fhir_id):
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            patient_url = f"{self.base_url}Patient/{fhir_id}"
            response = requests.get(patient_url, headers=headers)

            if response.status_code == 200:
                if 'application/xml' in response.headers.get('Content-Type', ''):
                    return self.parse_xml_patient_data(response.text)
                else:
                    error_message = "Unsupported response format"
                    current_app.logger.error(error_message)                
                    raise Exception("Unsupported response format")
            else:
                error_message = f"Failed to retrieve patient data: {response.text}, Status Code: {response.status_code}"
                current_app.logger.error(error_message)
                raise Exception(f"Failed to retrieve patient data: {response.text}")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_basic_patient_data: {e}")
            raise


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

    def get_medication_data(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        medication_url = f"{self.base_url}/MedicationRequest?patient={fhir_id}"
        try:
            response = requests.get(medication_url, headers=headers)
            current_app.logger.debug(f"Medication API Response: {response.text}")

            if response.status_code != 200:
                error_message = f"Failed to retrieve medication data: {response.text}, Status Code: {response.status_code}"
                current_app.logger.error(error_message)
                raise Exception(error_message)

            if not response.text:
                error_message = "Empty response received from medication data API"
                current_app.logger.error(error_message)
                raise Exception(error_message)

            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            medications = []
            for entry in root.findall('.//fhir:entry', ns):
                medication_display = entry.find('.//fhir:medicationReference/fhir:display', ns)
                if medication_display is not None:
                    medications.append(medication_display.attrib.get('value', 'Unknown medication'))
            return ', '.join(medications) if medications else ['Unknown medication']

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_medication_data: {e}")
            raise
    

    def get_allergy_data(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        allergy_url = f"{self.base_url}AllergyIntolerance?patient={fhir_id}"
        try:
            response = requests.get(allergy_url, headers=headers)

            if response.status_code != 200:
                error_message = f"Failed to retrieve allergy data: {response.text}, Status Code: {response.status_code}"
                current_app.logger.error(error_message)
                raise Exception(error_message)

            current_app.logger.debug(f"Allergy API Response: {response.text}")

            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            allergies = []
            for entry in root.findall('.//fhir:entry', ns):
                allergy_display = entry.find('.//fhir:AllergyIntolerance/fhir:code/fhir:coding/fhir:display', ns)
                if allergy_display is not None:
                    allergies.append(allergy_display.attrib.get('value', 'No known allergies'))
            return ', '.join(allergies) if allergies else ['No known allergies']

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_allergy_data: {e}")
            raise

        
    def get_condition_data(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        condition_url = f"{self.base_url}Condition?category=problem-list-item&clinical-status=active&patient={fhir_id}"
        try:
            response = requests.get(condition_url, headers=headers)

            if response.status_code != 200:
                error_message = f"Failed to retrieve condition data: {response.text}, Status Code: {response.status_code}"
                current_app.logger.error(error_message)
                raise Exception(error_message)

            current_app.logger.debug(f"Condition API Response: {response.text}")

            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            conditions = []
            for entry in root.findall('.//fhir:entry', ns):
                condition_text = entry.find('.//fhir:Condition/fhir:code/fhir:text', ns)
                if condition_text is not None:
                    conditions.append(condition_text.attrib.get('value', 'No known conditions'))
            return ', '.join(conditions) if conditions else ['No known conditions']

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_condition_data: {e}")
            raise


    def get_social_history_data(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        social_history_url = f"{self.base_url}Observation?patient={fhir_id}&category=social-history"
        try:
            response = requests.get(social_history_url, headers=headers)

            if response.status_code != 200:
                current_app.logger.error(f"Failed to retrieve social history data: {response.text}, Status Code: {response.status_code}")
                return "None"


            current_app.logger.debug(f"Social History API Response: {response.text}")

            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            social_histories = []
            for entry in root.findall('.//fhir:entry', ns):
                social_history_display = entry.find('.//fhir:Observation/fhir:valueCodeableConcept/fhir:coding/fhir:display', ns)
                if social_history_display is not None:
                    social_histories.append(social_history_display.attrib.get('value', 'No social history assessed'))
            return ', '.join(social_histories) if social_histories else ['No social history assessed']

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_social_history_data: {e}")
            return "None"
