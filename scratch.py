            for entry in root.findall('.//fhir:entry', ns):
                social_history_display = entry.find('.//fhir:Observation/fhir:valueCodeableConcept/fhir:coding/fhir:display', ns)
                if social_history_display is not None:
                    social_histories.append(social_history_display.attrib.get('value', 'No social history assessed'))

            for entry in root.findall('.//fhir:entry', ns):
                clinical_notes_content = entry.find('‘.//fhir:DocumentReference/fhir:content/fhir:attachment/fhir:url', ns)
                if clinical_notes_content is not None:
                    clinical_notes_content.append(social_history_display.attrib.get('value', 'No content'))

    try:
        headers = {'Authorization': f'Bearer {self.token}'}
        binary_clinical_notes_url = f"{self.base_url}{content_url}"

