class Protocol:

    def __init__(self):
        self.required_images = [('snr_acquisition_one',['TEST']),
                                ('snr_acquisition_two',['TEST']),
                                ('spir_water',['SPIR','WATER']),
                                ('spir_fat',['SPIR','FAT']),
                                ('spair_water',['SPAIR','WATER']),
                                ('spair_fat',['SPAIR', 'FAT']),
                                ('coil_one_acquisition_one',['COIL 1']),
                                ('coil_one_acquisition_two',['COIL 1']),
                                ('coil_two_acquisition_one',['COIL 2']),
                                ('coil_two_acquisition_two',['COIL 2']),
                                ('coil_three_acquisition_one',['COIL 3']),
                                ('coil_three_acquisition_two',['COIL 3']),
                                ('coil_four_acquisition_one',['COIL 4']),
                                ('coil_four_acquisition_two',['COIL 4']),
                                ('coil_five_acquisition_one',['COIL 5']),
                                ('coil_five_acquisition_two',['COIL 5']),
                                ('coil_six_acquisition_one',['COIL 6']),
                                ('coil_six_acquisition_two',['COIL 6']),
                                ('coil_seven_acquisition_one',['COIL 7']),
                                ('coil_seven_acquisition_two',['COIL 7']),
        ]
        self.dict_protocol_instances = {}
        for obj in self.required_images:
            self.dict_protocol_instances[obj[0]] = None

    def assign_instances_to_protocol(self, list_instances):
        for instance in list_instances:
            if ('COIL 1' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_one_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_one_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_one_acquisition_two'] = instance
            if ('COIL 2' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_two_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_two_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_two_acquisition_two'] = instance
            if ('COIL 3' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_three_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_three_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_three_acquisition_two'] = instance
            if ('COIL 4' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_four_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_four_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_four_acquisition_two'] = instance
            if ('COIL 5' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_five_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_five_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_five_acquisition_two'] = instance
            if ('COIL 6' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_six_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_six_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_six_acquisition_two'] = instance
            if ('COIL 7' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['coil_seven_acquisition_one'] is None):
                    self.dict_protocol_instances['coil_seven_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['coil_seven_acquisition_two'] = instance
            if ('SPAIR' in instance['SeriesDescription']):
                if ('WATER' in instance['SeriesDescription']):
                    self.dict_protocol_instances['spair_water'] = instance
                if ('FAT' in instance['SeriesDescription']):
                    self.dict_protocol_instances['spair_fat'] = instance
            if ('SPIR' in instance['SeriesDescription']):
                if ('WATER' in instance['SeriesDescription']):
                    self.dict_protocol_instances['spir_water'] = instance
                if ('FAT' in instance['SeriesDescription']):
                    self.dict_protocol_instances['spir_fat'] = instance
            if ('TEST' in instance['SeriesDescription']):
                if(self.dict_protocol_instances['snr_acquisition_one'] is None):
                    self.dict_protocol_instances['snr_acquisition_one'] = instance
                else:
                    self.dict_protocol_instances['snr_acquisition_two'] = instance
        missing_acquisitions =[]
        for k, v in self.dict_protocol_instances.iteritems():
            if v is None:
                missing_acquisitions.append(k)
        return missing_acquisitions
