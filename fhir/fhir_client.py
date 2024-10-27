# fhir/fhir_client.py
import requests
import xml.etree.ElementTree as ET
from xml.etree import ElementTree as ET
from flask import current_app
import datetime  # Import the datetime module
import json
import base64
from striprtf.striprtf import rtf_to_text
import urllib.parse
from PyPDF2 import PdfReader
import io
import csv
import os

class FhirClient:
    def __init__(self):
        self.base_url = session.get('hospital_endpoint', current_app.config['DEFAULT_EPIC_FHIR_BASE_URL'])
        self.token = None

    def get_fhir_id(self, mrn):
        headers = {'Authorization': f'Bearer {self.token}'}
        patient_id_url = f"{self.base_url}/Patient?identifier=MRN|{mrn}"
        try:
            response = requests.get(patient_id_url, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve patient FHIR ID: {response.text}, Status Code: {response.status_code}")

            current_app.logger.debug(f"Patient Search API Response: {response.text}")
            
            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            fhir_id = root.find('.//fhir:Patient/fhir:id', ns)
            return fhir_id.attrib['value'] if fhir_id is not None else None
        except requests.exceptions.RequestException as e:
            raise
    
    def get_patient_data_by_fhir_id(self, fhir_id):
        try:
            if not self.token:
                raise Exception("Authentication required")

            patient_data = self.get_basic_patient_data(fhir_id)
            patient_data['medications'] = self.get_medication_data(fhir_id)
            patient_data['allergies'] = self.get_allergy_data(fhir_id)
            patient_data['conditions'] = self.get_condition_data(fhir_id)
            patient_data['social_history'] = self.get_social_history_data(fhir_id)
            #patient_data['appointments'] = self.get_appointment_data(fhir_id)

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
        condition_url = f"{self.base_url}Condition?patient={fhir_id}" #removed category=problem-list-item&clinical-status=active&
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
        
    def process_pdf_content(self, pdf_binary, pdf_filename):
        try:
            # Save binary data as a PDF file
            pdf_filepath = f"/Users/samjohnson/CurnexaHealthAI/data/Clinical_Notes_PDFs/{pdf_filename}"
            with open(pdf_filepath, 'wb') as pdf_file:
                pdf_file.write(pdf_binary)
            current_app.logger.info(f"PDF saved locally: {pdf_filepath}")

            # Read and process PDF content using PyPDF2
            pdf_file = io.BytesIO(pdf_binary)
            pdf_reader = PdfReader(pdf_file)  # Use PdfReader here
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            pdf_file.close()

            current_app.logger.debug(f"Extracted PDF content: {text}")
            return text
        except Exception as e:
            current_app.logger.error(f"Error processing PDF: {e}")
            return "Error processing PDF content."


    def get_all_clinical_notes_content(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        doc_ref_url = f"{self.base_url}/DocumentReference"
        params = {'patient': fhir_id}  # removed, 'category': 'clinical-note' to see if we get other document types
        ns = {'fhir': 'http://hl7.org/fhir'}
        clinical_notes_contents = []

        def process_page(url):
            current_app.logger.debug(f"Calling DocumentReference API: {url}")
            response = requests.get(url, headers=headers)
            current_app.logger.debug(f"DocumentReference API Response: {response.text}")

            if response.status_code != 200:
                raise Exception(f"Failed to retrieve DocumentReference: {response.text}, Status Code: {response.status_code}")

            root = ET.fromstring(response.text)
            for entry in root.findall('.//fhir:entry', ns):
                content_elements = entry.findall('.//fhir:DocumentReference/fhir:content/fhir:attachment/fhir:url', ns)
                for content_element in content_elements:
                    if content_element is not None:
                        binary_relative_url = content_element.attrib.get('value')
                        if binary_relative_url:
                            binary_url = f"{self.base_url}/{binary_relative_url}"
                            current_app.logger.debug(f"Attempting to fetch content from Binary URL: {binary_url}")

                            binary_response = requests.get(binary_url, headers={
                                'Authorization': f'Bearer {self.token}',
                                'Accept': 'application/fhir+json'
                            })
                            current_app.logger.debug(f"Binary.read API Response for URL {binary_url}: {binary_response.text}")

                            content_data = binary_response.json()
                            content_type = content_data.get('contentType', '')
                            encoded_content = content_data.get('data', '')

                            if content_type in ['text/rtf', 'application/xml']:
                                decoded_content = base64.b64decode(encoded_content).decode('utf-8')
                                if content_type == 'application/xml':
                                    # Parse the XML content
                                    xml_root = ET.fromstring(decoded_content)
                                    xml_texts = [elem.text for elem in xml_root.iter() if elem.text]
                                    decoded_content = ' '.join(filter(None, xml_texts))
                                elif 'pdf' in decoded_content.lower():
                                    # Process PDF content
                                    pdf_binary = base64.b64decode(encoded_content)
                                    pdf_filename = f"pdf_{entry.find('.//fhir:id', ns).attrib.get('value')}.pdf"
                                    decoded_content = self.process_pdf_content(pdf_binary, pdf_filename)
                                elif content_type == 'text/rtf':
                                    try:
                                        decoded_content = rtf_to_text(decoded_content)
                                    except Exception as e:
                                        current_app.logger.error(f"Error processing RTF content: {e}")
                                        decoded_content = "Error processing RTF content."
                                clinical_notes_contents.append(decoded_content)
                            else:
                                current_app.logger.debug(f"Skipped content of type: {content_type}")

            next_link = root.find(".//fhir:link[@relation='next']", ns)
            return next_link.get('url') if next_link is not None else None

        try:
            next_page_url = process_page(doc_ref_url + '?' + urllib.parse.urlencode(params))
            while next_page_url:
                next_page_url = process_page(next_page_url)
            return clinical_notes_contents
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request exception: {e}")
            raise

    def fetch_patient_observations(self, fhir_id, mrn):
        headers = {'Authorization': f'Bearer {self.token}'}
        observation_url = f"{self.base_url}/Observation?patient={fhir_id}&category=laboratory"
        
        current_app.logger.debug("About to fetch laboratory observations")
        response = requests.get(observation_url, headers=headers)
        current_app.logger.debug(f"Raw API Response: {response.text}")  # Log the raw response text
        if response.status_code == 200:
            current_app.logger.debug("Successfully fetched laboratory observations.")
            try:
                root = ET.fromstring(response.content)
                ns = {'fhir': 'http://hl7.org/fhir'}
                observations = []

                for entry in root.findall('.//fhir:entry', ns):
                    observation = entry.find('.//fhir:Observation', ns)
                    if observation is not None:
                        coding_element = observation.find('.//fhir:code/fhir:coding', ns)
                        system = coding_element.find('.//fhir:system', ns).attrib['value']
                        code = coding_element.find('.//fhir:code', ns).attrib['value']
                        test_name = coding_element.find('.//fhir:display', ns).attrib['value']

                        value_element = observation.find('.//fhir:valueQuantity/fhir:value', ns)
                        unit_element = observation.find('.//fhir:valueQuantity/fhir:unit', ns)
                        result_value = value_element.attrib['value'] if value_element is not None else 'No result'
                        unit = unit_element.attrib['value'] if unit_element is not None else ''

                        low_element = observation.find('.//fhir:referenceRange/fhir:low/fhir:value', ns)
                        high_element = observation.find('.//fhir:referenceRange/fhir:high/fhir:value', ns)
                        low_value = low_element.attrib['value'] if low_element is not None else ''
                        high_value = high_element.attrib['value'] if high_element is not None else ''

                        observation_data = {
                            'MRN': mrn,
                            'system': system,
                            'code': code,
                            'test_name': test_name,
                            'result_value': result_value,
                            'high_value': high_value,
                            'low_value': low_value,
                            'units': unit
                        }
                        observations.append(observation_data)

                self.update_lab_data_csv(observations)
                return observations
            except ET.ParseError as e:
                current_app.logger.error(f"XML parsing error: {e}")
                return {"error": f"XML parsing error: {e}"}
        else:
            current_app.logger.error(f"Failed to fetch laboratory observations: {response.status_code}")
            return None
    
    def update_lab_data_csv(self, observations):
        csv_file_path = 'data/Labs/lab_data.csv'
        fieldnames = ['MRN', 'system', 'code', 'test_name', 'result_value', 'high_value', 'low_value', 'units']
        
        # Check if file exists and read existing data
        if os.path.exists(csv_file_path):
            with open(csv_file_path, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_data = [row for row in reader]
        else:
            existing_data = []

        # Append new observations if not duplicate
        with open(csv_file_path, mode='a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not existing_data:  # If file was empty, write header
                writer.writeheader()
            for observation in observations:
                if observation not in existing_data:
                    writer.writerow(observation)
        
    def fetch_patient_procedures(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        procedure_url = f"{self.base_url}/Procedure?patient={fhir_id}"
        
        current_app.logger.debug("About to fetch patient procedures")
        response = requests.get(procedure_url, headers=headers)
        if response.status_code == 200:
            current_app.logger.debug("Successfully fetched patient procedures.")
            try:
                root = ET.fromstring(response.content)
                ns = {'fhir': 'http://hl7.org/fhir'}
                procedures = []

                for entry in root.findall('.//fhir:entry', ns):
                    procedure = entry.find('.//fhir:Procedure', ns)
                    if procedure is not None:
                        procedure_data = {
                            'id': procedure.find('.//fhir:id', ns).attrib['value'] if procedure.find('.//fhir:id', ns) is not None else 'No ID',
                            'status': procedure.find('.//fhir:status', ns).attrib['value'] if procedure.find('.//fhir:status', ns) is not None else 'No status',
                            'category': procedure.find('.//fhir:category/fhir:coding/fhir:display', ns).attrib['value'] if procedure.find('.//fhir:category/fhir:coding/fhir:display', ns) is not None else 'No category',
                            'code_display': procedure.find('.//fhir:code/fhir:coding/fhir:display', ns).attrib['value'] if procedure.find('.//fhir:code/fhir:coding/fhir:display', ns) is not None else 'No code display',
                            'subject': procedure.find('.//fhir:subject/fhir:display', ns).attrib['value'] if procedure.find('.//fhir:subject/fhir:display', ns) is not None else 'No subject',
                            'encounter': procedure.find('.//fhir:encounter/fhir:display', ns).attrib['value'] if procedure.find('.//fhir:encounter/fhir:display', ns) is not None else 'No encounter',
                            'performedDateTime': procedure.find('.//fhir:performedDateTime', ns).attrib['value'] if procedure.find('.//fhir:performedDateTime', ns) is not None else 'No performed date',
                            'performers': [performer.find('.//fhir:actor/fhir:display', ns).attrib['value'] for performer in procedure.findall('.//fhir:performer', ns) if performer.find('.//fhir:actor/fhir:display', ns) is not None],
                            'reason_code': procedure.find('.//fhir:reasonCode/fhir:coding/fhir:display', ns).attrib['value'] if procedure.find('.//fhir:reasonCode/fhir:coding/fhir:display', ns) is not None else 'No reason code',
                        }
                        procedures.append(procedure_data)

                return procedures
            except ET.ParseError as e:
                current_app.logger.error(f"XML parsing error: {e}")
                return {"error": f"XML parsing error: {e}"}
        else:
            current_app.logger.error(f"Failed to fetch patient procedures: {response.status_code}")
            return None
        
    def fetch_patient_appointments(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        appointment_url = f"{self.base_url}/Appointment?patient={fhir_id}"

        current_app.logger.debug("About to fetch patient appointments")
        response = requests.get(appointment_url, headers=headers)
        if response.status_code == 200:
            current_app.logger.debug("Successfully fetched patient appointments.")
            try:
                root = ET.fromstring(response.content)
                ns = {'fhir': 'http://hl7.org/fhir'}
                appointments = []

                for entry in root.findall('.//fhir:entry', ns):
                    appointment = entry.find('.//fhir:Appointment', ns)
                    if appointment is not None:
                        participants_details = []
                        for participant in appointment.findall('.//fhir:participant', ns):
                            participant_type = participant.find('.//fhir:type/fhir:coding/fhir:display', ns)
                            participant_actor = participant.find('.//fhir:actor/fhir:display', ns)
                            participants_details.append({
                                'type': participant_type.attrib['value'] if participant_type is not None else 'No type',
                                'status': participant.find('.//fhir:status', ns).attrib['value'] if participant.find('.//fhir:status', ns) is not None else 'No status',
                                'actor_display': participant_actor.attrib['value'] if participant_actor is not None else 'No actor display',
                            })

                        appointments.append({
                            'id': appointment.find('.//fhir:id', ns).attrib['value'] if appointment.find('.//fhir:id', ns) is not None else 'No ID',
                            'status': appointment.find('.//fhir:status', ns).attrib['value'] if appointment.find('.//fhir:status', ns) is not None else 'No status',
                            'description': appointment.find('.//fhir:description', ns).attrib['value'] if appointment.find('.//fhir:description', ns) is not None else 'No description',
                            'start': appointment.find('.//fhir:start', ns).attrib['value'] if appointment.find('.//fhir:start', ns) is not None else 'No start date',
                            'end': appointment.find('.//fhir:end', ns).attrib['value'] if appointment.find('.//fhir:end', ns) is not None else 'No end date',
                            'participants': participants_details,
                        })

                return appointments
            except ET.ParseError as e:
                current_app.logger.error(f"XML parsing error: {e}")
                return {"error": f"XML parsing error: {e}"}
        else:
            current_app.logger.error(f"Failed to fetch patient appointments: {response.status_code}")
            return None
        
    def fetch_patient_diagnostic_reports(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        diagnostic_report_url = f"{self.base_url}/DiagnosticReport?patient={fhir_id}"
        
        current_app.logger.debug("About to fetch patient diagnostic reports")
        response = requests.get(diagnostic_report_url, headers=headers)
        if response.status_code == 200:
            current_app.logger.debug("Successfully fetched patient diagnostic reports.")
            try:
                root = ET.fromstring(response.content)
                ns = {'fhir': 'http://hl7.org/fhir'}
                diagnostic_reports = []

                for entry in root.findall('.//fhir:entry', ns):
                    report = entry.find('.//fhir:DiagnosticReport', ns)
                    if report is not None:
                        identifiers = report.findall('.//fhir:identifier/fhir:value', ns)
                        identifier_values = [identifier.attrib['value'] for identifier in identifiers if identifier is not None]

                        status = report.find('.//fhir:status', ns)
                        status_value = status.attrib['value'] if status is not None else 'No status'

                        category_coding = report.find('.//fhir:category/fhir:coding', ns)
                        category_display = category_coding.find('.//fhir:display', ns).attrib['value'] if category_coding is not None and category_coding.find('.//fhir:display', ns) is not None else 'No category'

                        code_coding = report.find('.//fhir:code/fhir:coding', ns)
                        code_display = code_coding.find('.//fhir:display', ns).attrib['value'] if code_coding is not None and code_coding.find('.//fhir:display', ns) is not None else 'No code display'

                        subject_reference = report.find('.//fhir:subject/fhir:display', ns)
                        subject_reference_value = subject_reference.attrib['value'] if subject_reference is not None else 'No subject'

                        encounter_reference = report.find('.//fhir:encounter/fhir:display', ns)
                        encounter_reference_value = encounter_reference.attrib['value'] if encounter_reference is not None else 'No encounter'

                        effectiveDateTime = report.find('.//fhir:effectiveDateTime', ns)
                        effectiveDateTime_value = effectiveDateTime.attrib['value'] if effectiveDateTime is not None else 'Unknown date'

                        report_data = {
                            'identifier': ', '.join(identifier_values),
                            'status': status_value,
                            'category': category_display,
                            'code_display': code_display,
                            'subject_reference': subject_reference_value,
                            'encounter_reference': encounter_reference_value,
                            'effectiveDateTime': effectiveDateTime_value,
                        }
                        diagnostic_reports.append(report_data)

                return diagnostic_reports
            except ET.ParseError as e:
                current_app.logger.error(f"XML parsing error: {e}")
                return {"error": f"XML parsing error: {e}"}
        else:
            current_app.logger.error(f"Failed to fetch patient diagnostic reports: {response.status_code}")
            return None

        
    

    '''def get_appointment_data(self, fhir_id):
        headers = {'Authorization': f'Bearer {self.token}'}
        appointment_url = f"{self.base_url}/Appointment?patient={fhir_id}&service-category=appointment"
        try:
            response = requests.get(appointment_url, headers=headers)
            if response.status_code != 200:
                error_message = f"Failed to retrieve appointment data: {response.text}, Status Code: {response.status_code}"
                current_app.logger.error(error_message)
                raise Exception(error_message)

            current_app.logger.debug(f"Appointment API Response: {response.text}")

            root = ET.fromstring(response.text)
            ns = {'fhir': 'http://hl7.org/fhir'}
            appointments = []
            for entry in root.findall('.//fhir:entry', ns):
                resource = entry.find('.//fhir:resource', ns)
                if resource is not None:
                    appointment = {
                        'reason': ', '.join([r.attrib.get('value', '') for r in resource.findall('.//fhir:reasonCode/fhir:text', ns)]),
                        'description': resource.find('.//fhir:description', ns).attrib.get('value', ''),
                        'start': resource.find('.//fhir:start', ns).attrib.get('value', ''),
                        'appointmentType': resource.find('.//fhir:appointmentType/fhir:text', ns).attrib.get('value', ''),
                        'serviceType': ', '.join([s.attrib.get('value', '') for s in resource.findall('.//fhir:serviceType/fhir:text', ns)]),
                        # Add more fields as necessary
                    }
                    appointments.append(appointment)

            return appointments

        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error in get_appointment_data: {e}")
            raise'''

