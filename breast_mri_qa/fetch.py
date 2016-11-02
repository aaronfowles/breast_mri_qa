""" This module deals with obtaining a dicom object from an Orthanc server.

"""
import numpy as np
import requests
import email
import dicom
import io
import sys
import json


class Fetcher:
    """ A Class to facilitate an object-oriented approach to querying the
        Orthanc server.
    """
    def __init__(self, host, port, user, passwd):
        """
        Class constructor will initialise class variables with appropriate
        values.

        These values specify the details required to connect to and authenticate
        with the Orthanc server.

        Parameters
        ----------
        host : String
            The v4 IP address of the Orthanc DICOM server.
            (e.g. `'192.168.0.3'`)
        port: int
            The port number that the Orthanc HTTP server is configured to
            run on. (e.g. `80`)
        user: String
            The username required to access the Orthanc server.
            (e.g. `'orthanc'`)
        passwd: String
            The password required to access the Orthanc server.
            (e.g. `'orthanc'`)
        Returns
        -------

        Examples
        --------
        >>> fetcher = Fetch(
            host=192.168.0.1,
            port=80,
            user='orthanc',
            passwd='orthanc'
        )
        >>>

        """
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.accept = {'Accept': 'application/json'}
        self.query = {}

    def get_studies_json(self, patient_name):
        """
        A function to obtain a JSON object describing the studies on the
        server which are associated with a patient name matching that supplied
        in `patient_name`.

        Parameters
        ----------
        patient_name: String
            A string used to match against patient names of the studies on the
            Orthanc server. You may include wildcards so that `'*BREAST*'` will
            retrieve details of all studies where the patient name contains
            'BREAST'.

        Returns
        -------
        matches: JSON
            A JSON object containing a list of matched studies with information
            such as date of study, name of patient etc...

        See Also
        --------
        Orthanc DICOMweb plugin -
        https://orthanc.chu.ulg.ac.be/book/plugins/dicomweb.html

        Examples
        --------
        >>> fetcher.get_studies_json('*BREAST*')
        [{'00080005': {'Value': ['ISO_IR 100'], 'vr': 'CS'},
            '00080020': {'Value': ['20160627'], 'vr': 'DA'},
            '00080030': {'Value': ['120515'], 'vr': 'TM'},
            '00080050': {'Value': [''], 'vr': 'SH'},
            '00080061': {'Value': ['MR'], 'vr': 'CS'},
            '00080090': {'Value': [''], 'vr': 'PN'},
        ...
        >>>
        """
        self.query = {'PatientName': patient_name}
        url = 'http://%s:%d/dicom-web/studies/' % (self.host, self.port)
        http_response = requests.get(
            url,
            auth=(self.user, self.passwd),
            headers=self.accept,
            params=self.query
        )
        matches = http_response.json()
        return matches

    def get_n_most_recent_study_details(self, patient_name, n_most_recent):
        json_studies = self.get_studies_json(patient_name=patient_name)
        studies = []
        for study in json_studies:
            c = {}
            c['StudyDate'] = study['00080020']['Value'][0]
            c['StudyUID'] = study['0020000D']['Value'][0]
            c['PatientName'] = study['00100010']['Value'][0]
            studies.append(c)
        studies = sorted(studies, key=lambda k: k['StudyDate'])
        return studies[:n_most_recent]


    def get_series(self, studyuid):
        url = 'http://%s:%d/dicom-web/studies/%s/series/' % (self.host, self.port, studyuid)
        http_response = requests.get(url, auth=(self.user, self.passwd), headers=self.accept, params=self.query)
        matches = http_response.json()
        seriesuids = [match['0020000E']['Value'][0] for match in matches]
        return seriesuids

    def get_valid_image_instance(self, studyuid, seriesuid):
        url = 'http://%s:%d/dicom-web/studies/%s/series/%s' % (self.host, self.port, studyuid, seriesuid)
        http_response = requests.get(url, auth=(self.user, self.passwd))
        # Construct valid mime by prepending content type
        if (sys.version_info[0] == 2):
            hdr = ('Content-Type: ' + http_response.headers['Content-Type'])
            msg =  email.message_from_string(hdr + b'\r\n' + http_response.content)
        else:
            hdr = ('Content-Type: ' + http_response.headers['Content-Type']).encode('UTF-8')
            msg =  email.message_from_bytes(hdr + b'\r\n' + http_response.content)
        dcmobjs = []
        for part in msg.walk():
            dcmdata = part.get_payload(decode=True)
            if dcmdata is not None:
                if (sys.version_info[0] == 2):
                    dcmobjs.append(dicom.read_file(io.BytesIO(dcmdata)))
                else:
                    dcmobjs.append(dicom.read_file(io.BytesIO(dcmdata)))
        ret_dcm_obj = dcmobjs[0]
        ret_dicom_dict = {}
        try:
            ret_dcm_obj[0x0008, 0x0008]  # Only images have image type header tag
            ret_dicom_dict['SeriesInstanceUID'] = ret_dcm_obj[0x0020, 0x000E].value
            ret_dicom_dict['SeriesDescription'] = ret_dcm_obj[0x0008, 0x103E].value
            ret_dicom_dict['StudyDescription'] = ret_dcm_obj[0x0008, 0x1030].value
            ret_dicom_dict['StudyInstanceUID'] = ret_dcm_obj[0x0020, 0x000D].value
            ret_dicom_dict['StudyDate'] = ret_dcm_obj[0x0008, 0x0020].value
            ret_dicom_dict['StationName'] = ret_dcm_obj[0x0008, 0x1010].value
            ret_dicom_dict['PatientName'] = ret_dcm_obj[0x0010, 0x0010].value
            ret_dicom_dict['PatientID'] = ret_dcm_obj[0x0010, 0x0020].value
            ret_dicom_dict['MagneticFieldStrength'] = ret_dcm_obj[0x0018, 0x0087].value
            ret_dicom_dict['PixelArray'] = ret_dcm_obj.pixel_array
        except Exception as ex:
            pass
        if ret_dicom_dict is None:
            pass
        else:
            if ret_dicom_dict:
                return ret_dicom_dict