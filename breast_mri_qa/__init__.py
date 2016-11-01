""" This package houses code for processing dicom images obtained from an
Orthanc server using its http protocol. As of v0.1.0 it will only work with
images obtained from a Phillips MRI machine and will need to be revised in
order to guarantee functional use with other manufacturers' machines. This is
mostly due to the fact that a multi-slice instance is represented as a single
dicom object by Phillips whereas this is not the case for other manufacturers. 
"""
