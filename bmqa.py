#! /usr/bin/python

from __future__ import absolute_import, division, print_function
from builtins import input

import argparse

from breast_mri_qa import fetch, organise, measure

parser = argparse.ArgumentParser()
parser.add_argument('--host', nargs=1, required=True)
parser.add_argument('--port', nargs=1, required=True, default=80)
parser.add_argument('--user', nargs=1, required=True, default='orthanc')
parser.add_argument('--passwd', nargs=1, required=True, default='orthanc')
parser.add_argument('--config', nargs=1, required=True, default='config.yml')

args = parser.parse_args()

rules_config_file = args.config[0]

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

protocol = organise.Protocol(rules_config_file)
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
