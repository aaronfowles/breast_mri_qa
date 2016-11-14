"""
This module allows a user to specify a protocol to ensure that a study
contains all the images required to do the QA analysis.
"""
import yaml

class Protocol:
    """
    Make Protocol objects.

    Parameters
    ----------
    rules_config_file : filepath to yaml config
        Each element of the rules list specifies the information required_images
        to determine how to match a dicom object to a protocol image.
        (e.g. The first item in the tuple specifies the name of the protocol image
        (e.g. 'snr_acquisition_one'), the second specifies the string used to match an
        image name to a protocol image (e.g.) 'SNR'.)

    Attributes
    -------
    required_images : Dictionary
        Key-value pairs of protocol image name and search terms derived from config.
    dict_protocol_instances : Dictionary
        Key-value pairs of protocol image name and Instance objects when used
        with the `assign_instances_to_protocol` function.
    """
    def __init__(self, rules_config_file):
        with open(rules_config_file) as ymlfile:
            cfg = yaml.load(ymlfile)
            rules = []
            rules = [rule for rule in cfg['name_identifier_pairs'].items()]
        self.required_images = rules
        self.dict_protocol_instances = {}
        for obj in self.required_images:
            self.dict_protocol_instances[obj[0]] = None

    def match_logic(self, search_term, instance):
        """
        Function used to checker whether an dicom object's name matches the
        naming convention required for that image in the protocol.

        Parameters
        ----------
        search_term : String
            String to search for in instance.series_description
        instance : Instance object

        Returns
        -------
        bool
            True if `search_term` occurs in SeriesDescription, False otherwise.
        """
        if search_term in instance.series_description:
            return True
        else:
            return False

    def save_instance(self, img_name, instance):
        """
        Saves the specified instance to the internal `dict_protocol_instances`
        object.

        Parameters
        ----------
        img_name : String
            Name to use as the identifying key in the `dict_protocol_instances`
            dictionary under which the image should be saved. This must match a
            valid protocol image name.
        instance : Instance object

        Returns
        -------
        bool
            True if image saved succesfully, False otherwise.
        """
        if self.dict_protocol_instances[img_name] is None and img_name in self.dict_protocol_instances.keys():
            self.dict_protocol_instances[img_name] = instance
            return True
        else:
            return False

    def assign_instances_to_protocol(self, list_instances):
        """
        Takes a list of Instances containing dicom object information and
        attempts to match them to the protocol.

        Parameters
        ----------
        list_instances : list of Instance objects.

        See Also
        --------
        Instance

        Returns
        -------
        missing_acquisitions : list of Strings
            Empty if there are enough images present in `list_instances` to
            form a complete protocol. Otherwise, each element in the list is the
            name of the protocol item not present.
        """
        for instance in list_instances:
            for img_name, search_term in self.required_images:
                if self.match_logic(search_term, instance):
                    if self.save_instance(img_name, instance):
                        break

        missing_acquisitions = []
        for k, v in self.dict_protocol_instances.items():
            if v is None:
                missing_acquisitions.append(k)
        return missing_acquisitions


class Instance:
    """
    Create an Instance object.

    An object to hold the pixel array and associated dicom meta-data
    of a dicom instance. In this context, an instance is a dicom object
    pertaining to a multi-slice MRI image acquisition where `self.pixel_array`
    is a 3-d numpy ndarray indexed by [z,y,x].

    Parameters
    ----------
    series_instance_uid : String
    series_description : String
    study_description : String
    study_instance_uid : String
    study_date : String
    station_name : String
    patient_name : String
    patient_id : String
    magnetic_field_strength : String
    pixel_array : 3-d ndarray

    Attributes
    ----------
    series_instance_uid : String
    series_description : String
    study_description : String
    study_instance_uid : String
    study_date : String
    station_name : String
    patient_name : String
    patient_id : String
    magnetic_field_strength : String
    pixel_array : 3-d ndarray
    """
    def __init__(
            self,
            series_instance_uid,
            series_description,
            study_description,
            study_instance_uid,
            study_date,
            station_name,
            patient_name,
            patient_id,
            magnetic_field_strength,
            pixel_array
            ):
        self.series_instance_uid = series_instance_uid
        self.series_description = series_description
        self.study_description = study_description
        self.study_instance_uid = study_instance_uid
        self.study_date = study_date
        self.station_name = station_name
        self.patient_name = patient_name
        self.patient_id = patient_id
        self.magnetic_field_strength = magnetic_field_strength
        self.pixel_array = pixel_array
