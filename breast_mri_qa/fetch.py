"""
This module deals with obtaining a dicom object from an Orthanc server.
"""
import io
import sys
import email
import json

import numpy as np
import requests
import dicom

from .organise import Instance


class Fetcher:
    """
    A Class to facilitate an object-oriented approach to querying the
    Orthanc server.

    Parameter values specify the details required to connect to and
    authenticate with the Orthanc server.

    Parameters
    ----------
    host : String
        The v4 IP address of the Orthanc DICOM server.
        (e.g. `'192.168.0.3'`)
    port : int
        The port number that the Orthanc HTTP server is configured to
        run on. (e.g. `80`)
    user : String
        The username required to access the Orthanc server.
        (e.g. `'orthanc'`)
    passwd : String
        The password required to access the Orthanc server.
        (e.g. `'orthanc'`)

    Attributes (object)
    ----------
    host : String
        The v4 IP address of the Orthanc DICOM server.
        (e.g. `'192.168.0.3'`)
    port : int
        The port number that the Orthanc HTTP server is configured to
        run on. (e.g. `80`)
    user : String
        The username required to access the Orthanc server.
        (e.g. `'orthanc'`)
    passwd : String
        The password required to access the Orthanc server.
        (e.g. `'orthanc'`)
    accept : dictionary
        MIME type used in the HTTP request header,
        default value is {'Accept': 'application/json'}
    """

    def __init__(self, host, port, user, passwd):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.accept = {'Accept': 'application/json'}

    def get_studies_json(self, patient_name):
        """
        A function to obtain a JSON object describing the studies on the
        server which are associated with a patient name matching that supplied
        in `patient_name`.

        Parameters
        ----------
        patient_name : String
            A string used to match against patient names of the studies on the
            Orthanc server. You may include wildcards so that `'*BREAST*'` will
            retrieve details of all studies where the patient name contains
            'BREAST'.

        Returns
        -------
        matches : JSON object
            A JSON object containing a list of matched studies with information
            such as date of study, name of patient etc...

        See Also
        --------
        Orthanc : https://orthanc.chu.ulg.ac.be/book/plugins/dicomweb.html

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
        query = {'PatientName': patient_name}
        url = 'http://{0}:{1}/dicom-web/studies/'.format(self.host, self.port)
        http_response = requests.get(
            url,
            auth=(self.user, self.passwd),
            headers=self.accept,
            params=query
        )
        matches = http_response.json()
        return matches

    def get_n_most_recent_study_details(self, patient_name, n_most_recent):
        """
        Gets the N most recent studies matching patient name criteria.

        This function extends get_studies_json by allowing an additional
        parameter specifying how many studies to return.

        Parameters
        ----------
        patient_name : String
            A string used to match against patient names of the studies on the
            Orthanc server. You may include wildcards so that `'*BREAST*'` will
            retrieve details of all studies where the patient name contains
            'BREAST'.
        n_most_recent : int
            The number of studies to return.

        Returns
        -------
        n_most_recent_studies : JSON object
            A JSON object containing a list of matched studies with information
            such as date of study, name of patient etc... The number of JSON
            objects in the list will be less than or equal to the parameter
            `n_most_recent`.
        """
        json_studies = self.get_studies_json(patient_name=patient_name)
        studies = []
        for study in json_studies:
            c = {}
            c['StudyDate'] = study['00080020']['Value'][0]
            c['StudyUID'] = study['0020000D']['Value'][0]
            c['PatientName'] = study['00100010']['Value'][0]
            studies.append(c)
        studies = sorted(studies, key=lambda k: k['StudyDate'])
        n_most_recent_studies = studies[:n_most_recent]
        return n_most_recent_studies

    def get_series(self, studyuid):
        """
        Get all series UIDs associated with a certain Study.

        Parameters
        ----------
        studyuid : String
            Study Instance UID as specified in the DICOM header by (0020,000D).

        Returns
        -------
        seriesuids : list of Strings
            A list of Series Instance UIDs as specified in the DICOM header
            by tag (0020,000E)

        """
        url = 'http://{}:{}/dicom-web/studies/{}/series/'.format(
            self.host,
            self.port,
            studyuid
        )
        http_response = requests.get(
            url,
            auth=(self.user, self.passwd),
            headers=self.accept
        )
        matches = http_response.json()
        seriesuids = [match['0020000E']['Value'][0] for match in matches]
        return seriesuids

    def get_valid_image_instance(self, studyuid, seriesuid):
        """
        Check whether a series contains a valid image instance and return
        it if so.

        Parameters
        ----------
        studyuid : String
            Study Instance UID as specified in the DICOM header by (0020,000D).
        seriesuid : String
            Series Instance UIDs as specified in the DICOM header by (0020,000E)

        Returns
        -------
        dicom_instance_info : dictionary
            A dictionary containing information from the instance object's
            headers in a human-readable form.

        Examples
        --------
        >>> dicom_instance_info = get_valid_image_instance(studyuid, seriesuid)
        >>> for k, v in dicom_instance_info.items():
        ...    print ((k, type(v)))
        ('StudyDate', <type 'str'>)
        ('MagneticFieldStrength', <type 'str'>)
        ('SeriesDescription', <type 'str'>)
        ('StudyDescription', <type 'str'>)
        ('PatientID', <type 'str'>)
        ('PixelArray', <type 'numpy.ndarray'>)
        ('StationName', <type 'str'>)
        ('StudyInstanceUID', <type 'str'>)
        ('SeriesInstanceUID', <type 'str'>)
        ('PatientName', <type 'str'>)
        """
        url = 'http://{}:{}/dicom-web/studies/{}/series/{}'.format(
            self.host,
            self.port,
            studyuid,
            seriesuid
        )
        http_response = requests.get(
            url,
            auth=(self.user, self.passwd)
        )
        # Construct valid mime by prepending content type
        if (sys.version_info[0] == 2):
            hdr = ('Content-Type: ' + http_response.headers['Content-Type'])
            msg = email.message_from_string(hdr + b'\r\n' + http_response.content)
        else:
            hdr = ('Content-Type: ' + http_response.headers['Content-Type']).encode('UTF-8')
            msg = email.message_from_bytes(hdr + b'\r\n' + http_response.content)
        dcmobjs = []
        for part in msg.walk():
            dcmdata = part.get_payload(decode=True)
            if dcmdata is not None:
                if (sys.version_info[0] == 2):
                    dcmobjs.append(dicom.read_file(io.BytesIO(dcmdata)))
                else:
                    dcmobjs.append(dicom.read_file(io.BytesIO(dcmdata)))
        # For Phillips scanners the dicom object is in the first element of the list
        dcm_obj = dcmobjs[0]
        # Create an instance object which will hold dicom instance pixel array and various headers
        instance = None
        try:
            dcm_obj[0x0008, 0x0008]  # Only images have image type header tag
            instance = Instance(
                series_instance_uid=str(dcm_obj[0x0020, 0x000E].value),
                series_description=dcm_obj[0x0008, 0x103E].value,
                study_description=dcm_obj[0x0008, 0x1030].value,
                study_instance_uid=str(dcm_obj[0x0020, 0x000D].value),
                study_date=dcm_obj[0x0008, 0x0020].value,
                station_name=dcm_obj[0x0008, 0x1010].value,
                patient_name=str(dcm_obj[0x0010, 0x0010].value),
                patient_id=dcm_obj[0x0010, 0x0020].value,
                magnetic_field_strength=str(dcm_obj[0x0018, 0x0087].value),
                pixel_array=dcm_obj.pixel_array
            )
        # If exception then the dicom object is not an image so do nothing
        except Exception as ex:
            pass

        # Don't return the empty instance
        if instance is None:
            pass
        else:
            if instance:
                return instance
