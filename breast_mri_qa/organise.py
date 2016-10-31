class Protocol:

    def __init__(self, rules):
        self.required_images = rules
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


    def assign_instances_to_protocol(self, list_instances):
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
