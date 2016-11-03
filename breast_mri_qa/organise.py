""" This module allows a user to specify a protocol to ensure that a study
contains all the images required to do the QA analysis.
"""

class Protocol:
    """ This class allows a user to specify and add images to a protocol.

    """
    def __init__(self, rules):
        """
        Constructor class for making Protocol objects.

        Parameters
        ----------
        rules : list of 3-tuples
            Each element of the rules list specifies the information required_images
            to determine how to match a dicom object to a protocol image.
            (e.g. The first item in the tuple specifies the name of the protocol image
            (e.g. 'snr_acquisition_one'), the second specifies the name
            of the function used to determine whether an image is appropriate
            (e.g. 'is_snr') and the third specifies the string used to match an
            image name to a protocol image (e.g.) 'SNR'.)

        Returns
        -------
        Protocol : Protocol object
        """
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
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if `search_term` occurs in SeriesDescription, False otherwise.
        """
        if search_term in instance['SeriesDescription']:
            return True
        else:
            return False

    def is_snr(self, search_term, instance):
        """
        Determines whether or not an image may be used as an SNR calulation
        image in the protocol.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if usable as an SNR image, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_spir_water_fse(self, search_term, instance):
        """
        Determines whether or not an image may be used for SPIR water
        suppression efficiency calulation.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if usable as an SPIR water suppression image, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_spir_fat_fse(self, search_term, instance):
        """
        Determines whether or not an image may be used for SPIR fat
        suppression efficiency calulation.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if usable as an SPIR fat suppression image, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_spair_water_fse(self, search_term, instance):
        """
        Determines whether or not an image may be used for SPAIR water
        suppression efficiency calulation.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if usable as an SPAIR water fat suppression image, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_spair_fat_fse(self, search_term, instance):
        """
        Determines whether or not an image may be used for SPAIR fat
        suppression efficiency calulation.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if usable as an SPAIR water fat suppression image, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_one(self, search_term, instance):
        """
        Determines whether or not an image is from coil one.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil one, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_two(self, search_term, instance):
        """
        Determines whether or not an image is from coil two.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil two, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_three(self, search_term, instance):
        """
        Determines whether or not an image is from coil three.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil three, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_four(self, search_term, instance):
        """
        Determines whether or not an image is from coil four.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil four, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_five(self, search_term, instance):
        """
        Determines whether or not an image is from coil five.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil five, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_six(self, search_term, instance):
        """
        Determines whether or not an image is from coil six.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil six, False otherwise.
        """
        return self.match_logic(search_term, instance)

    def is_coil_seven(self, search_term, instance):
        """
        Determines whether or not an image is from coil seven.

        Parameters
        ----------
        search_term : String
            String to search for in instance['SeriesDescription']
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if from coil seven, False otherwise.
        """
        return self.match_logic(search_term, instance)

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
        instance : dictionary
            Dictionary containing dicom instance information
        Returns
        -------
        Boolean
            True if image saved succesfully, False otherwise.
        """
        if self.dict_protocol_instances[img_name] is None and img_name in self.dict_protocol_instances.keys():
            self.dict_protocol_instances[img_name] = instance
            return True
        else:
            return False


    def assign_instances_to_protocol(self, list_instances):
        """
        Takes a list of dictionaries containing dicom object information
        and attempts to match them to the protocol.

        Parameters
        ----------
        list_instances : list of dictionaries containing dicom object information
            A list of dictionaries containing dicom object information.
        Returns
        -------
        missing_acquisitions : list of Strings
            Empty if there are enough images present in `list_instances` to
            form a complete protocol. Otherwise, each element in the list is the
            name of the protocol item not present.
        """
        for instance in list_instances:
            for img_name, match_func, search_term in self.required_images:
                match_func = eval('self.' + match_func)
                if match_func(search_term, instance):
                    if self.save_instance(img_name, instance):
                        break

        missing_acquisitions = []
        for k, v in self.dict_protocol_instances.items():
            if v is None:
                missing_acquisitions.append(k)
        return missing_acquisitions
