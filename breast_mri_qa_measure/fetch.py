import numpy as np
import requests
import email
import dicom
import io

class Fetcher:

    def __init__(self):
        self.host = '139.59.186.101'
        self.port = 80
        self.user = 'orthanc'
        self.passwd = 'orthanc'
        self.accept = {'Accept': 'application/json'}
        self.query = {}

    def get_studies_json(self, patient_id):
        self.query = {'PatientID': patient_id}
        url = 'http://%s:%d/dicom-web/studies/' % (self.host, self.port)
        http_response = requests.get(url, auth=(self.user, self.passwd), headers=self.accept, params=self.query)
        matches = http_response.json()
        return matches

    def get_studies(self, patient_id):
        self.query = {'PatientID': patient_id}
        url = 'http://%s:%d/dicom-web/studies/' % (self.host, self.port)
        http_response = requests.get(url, auth=(self.user, self.passwd), headers=self.accept, params=self.query)
        matches = http_response.json()
        studyuids = [match['0020000D']['Value'][0] for match in matches]
        return studyuids

    def get_series(self, studyuid):
        url = 'http://%s:%d/dicom-web/studies/%s/series/' % (self.host, self.port, studyuid)
        http_response = requests.get(url, auth=(self.user, self.passwd), headers=self.accept, params=self.query)
        matches = http_response.json()
        seriesuids = [match['0020000E']['Value'][0] for match in matches]
        return seriesuids

    def get_valid_image_instances(self, studyuid, seriesuid):
        url = 'http://%s:%d/dicom-web/studies/%s/series/%s' % (self.host, self.port, studyuid, seriesuid)
        http_response = requests.get(url, auth=(self.user, self.passwd))
        # Construct valid mime by prepending content type
        hdr = ('Content-Type: ' + http_response.headers['Content-Type']).encode()
        msg =  email.message_from_string(hdr + b'\r\n' + http_response.content)
        dcmobjs = []
        for part in msg.walk():
            dcmdata = part.get_payload(decode=True)
            if dcmdata is not None:
                dcmobjs.append(dicom.read_file(io.BytesIO(dcmdata)))
        for instance in dcmobjs:
            try:
                instance[0x0008,0x0008] # Only images should have image type header tag
            except:
                dcmobjs.remove(instance)
                continue
        return dcmobjs
