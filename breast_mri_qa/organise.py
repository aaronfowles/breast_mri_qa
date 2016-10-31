class Protocol:

    def __init__(self):
        self.required_images = [('snr_acquisition_one', self.is_snr, self.save_snr, 'TEST'),
                                ('snr_acquisition_two', self.is_snr, self.save_snr, 'TEST'),
                                ('spir_water', self.is_spir_water_fse, self.save_spir_water_fse, 'SPIR WATER'),
                                ('spir_fat', self.is_spir_fat_fse, self.save_spir_fat_fse, 'SPIR FAT'),
                                ('spair_water', self.is_spair_water_fse, self.save_spair_water_fse, 'SPAIR WATER'),
                                ('spair_fat', self.is_spair_fat_fse, self.save_spair_fat_fse, 'SPAIR FAT'),
                                ('coil_one_acquisition_one', self.is_coil_one, self.save_coil_one, 'COIL 1'),
                                ('coil_two_acquisition_two', self.is_coil_one, self.save_coil_one, 'COIL 1'),
                                ('coil_one_acquisition_two', self.is_coil_two, self.save_coil_one, 'COIL 2'),
                                ('coil_two_acquisition_one', self.is_coil_two, self.save_coil_one, 'COIL 2'),
                                ('coil_three_acquisition_one', self.is_coil_three, self.save_coil_one, 'COIL 3'),
                                ('coil_three_acquisition_two', self.is_coil_three, self.save_coil_one, 'COIL 3'),
                                ('coil_four_acquisition_one', self.is_coil_four, self.save_coil_one, 'COIL 4'),
                                ('coil_four_acquisition_two', self.is_coil_four, self.save_coil_one, 'COIL 4'),
                                ('coil_five_acquisition_one', self.is_coil_five, self.save_coil_one, 'COIL 5'),
                                ('coil_five_acquisition_two', self.is_coil_five, self.save_coil_one, 'COIL 5'),
                                ('coil_six_acquisition_one', self.is_coil_six, self.save_coil_one, 'COIL 6'),
                                ('coil_six_acquisition_two', self.is_coil_six, self.save_coil_one, 'COIL 6'),
                                ('coil_seven_acquisition_one', self.is_coil_seven, self.save_coil_one, 'COIL 7'),
                                ('coil_seven_acquisition_two', self.is_coil_seven, self.save_coil_one, 'COIL 7'),
        ]
        self.dict_protocol_instances = {}
        for obj in self.required_images:
            self.dict_protocol_instances[obj[0]] = None

    def match_logic(self, search_term, instance):
        if search_term in instance['SeriesDescription']:
            return True
        else:
            return False

    def is_snr(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_spir_water_fse(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_spir_fat_fse(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_spair_water_fse(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_spair_fat_fse(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_one(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_two(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_three(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_four(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_five(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_six(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def is_coil_seven(self, search_term, instance):
        return self.match_logic(search_term, instance)

    def save_instance(self, img_name, instance):
        if self.dict_protocol_instances[img_name] is None:
            self.dict_protocol_instances[img_name] = instance
            return True
        else:
            return False

    def save_snr(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_spir_water_fse(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_spir_fat_fse(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_spair_water_fse(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_spair_fat_fse(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_one(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_two(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_three(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_four(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_five(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_six(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def save_coil_seven(self, img_name, instance):
        return self.save_instance(img_name, instance)

    def assign_instances_to_protocol(self, list_instances):
        for instance in list_instances:
            for img_name, match_func, apply_func, search_term in self.required_images:
                if match_func(search_term, instance):
                    if apply_func(img_name, instance):
                        break

        missing_acquisitions = []
        for k, v in self.dict_protocol_instances.iteritems():
            if v is None:
                missing_acquisitions.append(k)
        return missing_acquisitions
