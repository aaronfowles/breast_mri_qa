# Breast MRI QA
This package contains code which may be used to automate various aspects of MRI Quality Assurance required for UK the national breast screening programme.

[![Documentation Status](https://readthedocs.org/projects/breast-mri-qa/badge/?version=1.0.0)](http://breast-mri-qa.readthedocs.io/en/1.0.0/?badge=1.0.0)
[![PyPI version](https://badge.fury.io/py/breast_mri_qa.svg)](https://badge.fury.io/py/breast_mri_qa)

## Notebook
The demonstrative notebook may be found [here](ExampleBreastMRI.ipynb).

## CLI
The following instructions will allow you to use the command line interface.
```
git clone https://github.com/aaronfowles/breast_mri_qa.git
cd breast_mri_qa
python bmqa.py --config config.yml
```

Follow the instructions.

## Configuration
The configuration for the CLI may be found [here](config.yml). It is written in
YAML. The `name_identifier_pairs` specify the name of an image in the protocol
and the corresponding search term used to identify an image type.


[Issue Tracker](https://github.com/aaronfowles/breast_mri_qa/issues)
