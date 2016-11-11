#! /usr/bin/python

from __future__ import absolute_import, division, print_function
from builtins import input

import argparse
import yaml
import collections

from breast_mri_qa import fetch, organise, measure

parser = argparse.ArgumentParser()
parser.add_argument('--config', nargs=1, required=True, default='config.yml')
args = parser.parse_args()

rules_config_file = args.config[0]

with open(rules_config_file) as ymlfile:
    cfg = yaml.load(ymlfile)
    params = cfg['connection_params']
    fetcher = fetch.Fetcher(
        host=params['host'],
        port=params['port'],
        user=params['user'],
        passwd=params['passwd']
    )
    rules = [rule for rule in cfg['name_identifier_pairs'].items()]

patient_name = input('Enter search term for patient name: ')
n_most_recent = 4
print('searching...')

studies = fetcher.get_n_most_recent_study_details(
    patient_name=patient_name,
    n_most_recent=n_most_recent
)

studyuids = [study['StudyUID'] for study in studies]
studies_for_select = []

print('The following studies were found.')

for study in studies:
    study_without_id = dict(study)
    del study_without_id['StudyUID']
    studies_for_select.append(study_without_id)

selection_options = zip([i for i in range(1, len(studies)+1)], studies_for_select)

for option in selection_options:
    print(option)

selected_study = input("Enter the number of the study you would like to use: ")
selection_index = int(selected_study) - 1

studyuid = studyuids[selection_index]
study = studies[selection_index]
seriesuids = fetcher.get_series(studyuid)

print('fetching instances...')
instances = list(filter(lambda x: x is not None, (fetcher.get_valid_image_instance(studyuid, uid) for uid in seriesuids)))
protocol = organise.Protocol(rules_config_file)
missing_instances = protocol.assign_instances_to_protocol(instances)
assert not missing_instances, missing_instances

images = protocol.dict_protocol_instances
study = collections.OrderedDict(study)

study['PatientID'] = instances[0].patient_id
study['StudyDescription'] = instances[0].study_description
study['StationName'] = instances[0].station_name
study['MagneticFieldStrength'] = instances[0].magnetic_field_strength

snr_results = measure.snr(measure.get_mid_slice(images['snr_acquisition_one'].pixel_array), measure.get_mid_slice(images['snr_acquisition_two'].pixel_array))
study['SNR_left'] = snr_results['left_snr']
study['SNR_right'] = snr_results['right_snr']

spir_results = measure.fse(measure.get_mid_slice(images['spir_fat'].pixel_array), measure.get_mid_slice(images['spir_water'].pixel_array))
study['SPIR-FSE_left'] = spir_results['left_fse']
study['SPIR-FSE_right'] = spir_results['right_fse']

spair_results = measure.fse(measure.get_mid_slice(images['spair_fat'].pixel_array), measure.get_mid_slice(images['spair_water'].pixel_array))
study['SPAIR-FSE_left'] = spair_results['left_fse']
study['SPAIR-FSE_right'] = spair_results['right_fse']

num_to_str = {'1':'one','2':'two','3':'three','4':'four','5':'five','6':'six','7':'seven'}
identifier = 'coil_{}_acquisition_one'
for row in enumerate(num_to_str.items()):
    study[identifier.format(row[1][1])] = '{:.2f}'.format(measure.get_mid_slice(images[identifier.format(row[1][1])].pixel_array).mean())

print(study)

import csv
import os.path
csv_dir = 'results'
csv_filename = study['StationName'] + '_' + study['StudyDate'] + '.csv'
csv_rel_path = os.path.join(csv_dir, csv_filename)
with open(csv_rel_path, 'w', newline='') as f:
    csv_file = csv.writer(f)
    csv_file.writerow(study.keys())
    csv_file.writerow(study.values())
    print('results saved in ' + os.path.abspath(os.path.curdir) + str(csv_rel_path))
