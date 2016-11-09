#! /usr/bin/python

from __future__ import absolute_import, division, print_function
from builtins import input

import argparse

from breast_mri_qa import fetch, organise, measure

parser = argparse.ArgumentParser()
parser.add_argument('--host', nargs=1, required=True)
parser.add_argument('--port', nargs=1, required=True)
parser.add_argument('--user', nargs=1, required=True)
parser.add_argument('--passwd', nargs=1, required=True)

args = parser.parse_args()

fetcher = fetch.Fetcher(
    host=args.host[0],
    port=args.port[0],
    user=args.user[0],
    passwd=args.passwd[0]
)
patient_name = input('Enter search term for patient name: ')
n_most_recent = 4

studies = fetcher.get_n_most_recent_study_details(
    patient_name=patient_name,
    n_most_recent=n_most_recent
)
studyuids = [study['StudyUID'] for study in studies]
print('The following studies were found.')
selection_options = zip([i for i in range(1, len(studies)+1)], studies)
for option in selection_options:
    print(option)
selected_study = input("Enter the number of the study you would like to use.")
selection_index = int(selected_study) - 1

studyuid = studyuids[selection_index]
study = studies[selection_index]
seriesuids = fetcher.get_series(studyuid)
print('fetching instances...')
instances = list(filter(lambda x: x is not None, (fetcher.get_valid_image_instance(studyuid, uid) for uid in seriesuids)))

rules = [
    ('snr_acquisition_one', 'is_snr', 'TEST'),
    ('snr_acquisition_two', 'is_snr', 'TEST'),
    ('spir_water', 'is_spir_water_fse', 'SPIR WATER'),
    ('spir_fat', 'is_spir_fat_fse', 'SPIR FAT'),
    ('spair_water', 'is_spair_water_fse', 'SPAIR WATER'),
    ('spair_fat', 'is_spair_fat_fse', 'SPAIR FAT'),
    ('coil_one_acquisition_one', 'is_coil_one', 'COIL 1'),
    ('coil_two_acquisition_two', 'is_coil_one', 'COIL 1'),
    ('coil_one_acquisition_two', 'is_coil_two', 'COIL 2'),
    ('coil_two_acquisition_one', 'is_coil_two', 'COIL 2'),
    ('coil_three_acquisition_one', 'is_coil_three', 'COIL 3'),
    ('coil_three_acquisition_two', 'is_coil_three', 'COIL 3'),
    ('coil_four_acquisition_one', 'is_coil_four', 'COIL 4'),
    ('coil_four_acquisition_two', 'is_coil_four', 'COIL 4'),
    ('coil_five_acquisition_one', 'is_coil_five', 'COIL 5'),
    ('coil_five_acquisition_two', 'is_coil_five', 'COIL 5'),
    ('coil_six_acquisition_one', 'is_coil_six', 'COIL 6'),
    ('coil_six_acquisition_two', 'is_coil_six', 'COIL 6'),
    ('coil_seven_acquisition_one', 'is_coil_seven', 'COIL 7'),
    ('coil_seven_acquisition_two', 'is_coil_seven', 'COIL 7'),
]
protocol = organise.Protocol(rules)
missing_instances = protocol.assign_instances_to_protocol(instances)
assert not missing_instances, missing_instances

get_mid_slice = measure.get_mid_slice
images = protocol.dict_protocol_instances
study['SNR'] = measure.snr(get_mid_slice(images['snr_acquisition_one'].pixel_array), get_mid_slice(images['snr_acquisition_two'].pixel_array))
study['SPIR-FSE'] = measure.fse(get_mid_slice(images['spir_fat'].pixel_array), get_mid_slice(images['spir_water'].pixel_array))
study['SPAIR-FSE'] = measure.fse(get_mid_slice(images['spair_fat'].pixel_array), get_mid_slice(images['spair_water'].pixel_array))
num_to_str = {'1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven'}
identifier = 'coil_{}_acquisition_one'
for row in enumerate(num_to_str.items()):
    study[identifier.format(row[1][1])] = '{:.2f}'.format(get_mid_slice(images[identifier.format(row[1][1])].pixel_array).mean())

study['StudyDescription'] = instances[0].study_description
study['StationName'] = instances[0].station_name
study['PatientID'] = instances[0].patient_id
study['MagneticFieldStrength'] = instances[0].magnetic_field_strength
print(study)

import csv
import os.path
csv_dir = 'results'
csv_filename = study['StationName'] + '_' + study['StudyDate'] + '.csv'
csv_rel_path = os.path.join(csv_dir,csv_filename)
with open(csv_rel_path, 'w') as f:
    csv_file = csv.writer(f)
    csv_file.writerow(study.keys())
    csv_file.writerow(study.values())
