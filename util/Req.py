import json

import requests

header = {"Accept": "application/fhir+json"}
patient_info_url = "https://hapi.fhir.org/baseR4/Patient"
medication_statement_info_url = "https://hapi.fhir.org/baseR4/MedicationStatement/"

class Req:

    @staticmethod
    def get(url: str, data=None):
        return requests.get(url, headers=header, params=data).json()

    @staticmethod
    def post(url: str, data=None):
        return requests.post(url, headers=header, data=json.dumps(data)).json()


if __name__ == "__main__":
    response = Req.get(medication_statement_info_url, {"patient": "30163"})
    print(json.dumps(response['entry'][0]['resource']['dosage'][0]['text']))
