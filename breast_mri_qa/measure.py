"""
This module contains functions used to make the calculations required for QA.
"""

import os
from math import sqrt, ceil

import dicom
import numpy as np

from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import binary_erosion, binary_dilation


def calculate_efficiency(fat_suppressed, water_suppressed, roi):
    """
    Helper function to calculate suppresion efficiency.

    Parameters
    ----------
    fat_suppressed : 2-d numpy array
        2-d numpy array representing the fat suppressed image slice. Element
        values in range [0-255].
    water_suppressed: 2-d numpy array
        2-d numpy array representing the water suppressed image slice. Element
        values in range [0-255].
    roi : 2-d numpy array
        2-d numpy array representing the water suppressed image slice. Element
        values are 1 if element is in region of interest and 0 otherwise.
    Returns
    -------
    suppression_efficiency : float
        Unformatted float giving the suppression efficiency calculated using
        the following formula:
        100*(fat_suppressed_mean - water_suppressed_mean)/fat_suppressed
    """
    fat_suppressed = fat_suppressed.copy()
    fat_suppressed_mean_pixel_value = fat_suppressed[roi.astype(bool)].mean()

    water_suppressed = water_suppressed.copy()
    water_suppressed_mean_pixel_value = water_suppressed[roi.astype(bool)].mean()

    suppression_efficiency = 100 * ((fat_suppressed_mean_pixel_value - water_suppressed_mean_pixel_value) / fat_suppressed_mean_pixel_value)
    return suppression_efficiency


def find_roi(region, roi_proportion):
    """
    Helper function to find the region of interest.

    Parameters
    ----------
    region : 2-d numpy ndarray
        Numpy area indicating region containing part of the test phantom
        object. Elements with a value of 1 indicate parts of the image which
        contain the feature, otherwise elements are 0.
    roi_proportion : float
        Value in the range [0-1] indicating proportion of `region` to select
        as the region of interest.
    Returns
    -------
    roi : 2-d numpy ndarray
        Numpy area indicating region containing part of the test phantom
        object to be used as the ROI. Elements with a value of 1 indicate parts
        of the image which contain the feature, otherwise elements are 0.
    """
    region_area = regionprops(region)[0].area
    target_roi_area = roi_proportion * region_area
    actual_roi_proportion = 1
    roi = region.copy()
    while actual_roi_proportion > roi_proportion:
        roi = binary_erosion(roi).astype(int)
        actual_roi_proportion = regionprops(roi)[0].area / float(region_area)
    return roi


def assign_regions(image_array):
    """
    Helper function assign left and right regions of test object.

    Parameters
    ----------
    image_array : 2-d numpy ndarray
        2-d numpy array to be used
    Returns
    -------
    regions : dictionary
        Dictionary containing two keys, left and right which contain references
        to the respective 2-d arrays used to represent each region.
    """
    img_height = image_array.shape[0]
    img_width = image_array.shape[1]

    otsu_thresh = threshold_otsu(image_array)
    np_mask = image_array > otsu_thresh
    # Recode booleans as integers
    np_mask = np_mask.astype(int)
    # Remove lower parts of phantom from mask
    np_mask[(int(0.75*(img_height))):, :] = 0
    regions = label(np_mask)
    region_1 = (regions == 1).astype(int)
    region_2 = (regions == 2).astype(int)
    left_region = None
    right_region = None
    regionprops(region_1)[0].centroid[1]
    # region centroid (x) > half-way point
    if (regionprops(region_1)[0].centroid[1] > img_width / 2):
        left_region = region_1
        right_region = region_2
    else:
        left_region = region_2
        right_region = region_1

    regions = {'left': left_region, 'right': right_region}
    return regions


def get_mid_slice(pixel_array):
    """
    Helper function to obtain the middle slice of a 3-d numpy ndarray.

    Parameters
    ----------
    pixel_array : 3-d numpy ndarray
        3-d array of form [z, y, x].

    Returns
    -------
    pixel_array : 2-d numpy ndarray
        A 2-d numpy array [y,x] of the middle slice from the 3-d input array
    """
    if len(pixel_array) <= 1:
        # Nonsense to get middle slice in this case
        return pixel_array
    return pixel_array[int(len(pixel_array) / float(2))]


def fse(fat_suppressed, water_suppressed, roi_proportion=0.8):
    """
    Calculate fat suppression efficiency.

    Parameters
    ----------
    fat_suppressed : 2-d ndarray
    water_suppressed : 2-d ndarray
    roi_proportion : float

    Returns
    -------
    fse_results : dictionary of floats
        `fse_results['left_fse']` contains a float indicating the results for
        the left region. It is in the range [0-100]. `fse_results['right_fse']`
        contains a float indicating the results for the right region.
        It is also in the range [0-100].
    """
    fse_results = {'left_fse': None, 'right_fse': None}

    regions = assign_regions(fat_suppressed)
    left_region = regions['left']
    right_region = regions['right']

    left_roi = find_roi(left_region, roi_proportion)
    right_roi = find_roi(right_region, roi_proportion)

    # Left Suppression efficiency
    fse_results['left_fse'] = calculate_efficiency(
        fat_suppressed,
        water_suppressed,
        left_roi
    )
    fse_results['right_fse'] = calculate_efficiency(
        fat_suppressed,
        water_suppressed,
        right_roi
    )
    return fse_results


def snr(unsuppressed_one, unsuppressed_two, roi_proportion=0.8):
    """
    Calculate the signal-to-noise ratio.

    Parameters
    ----------
    unsuppressed_one : 2-d ndarray
    unsuppressed_two : 2-d ndarray
    roi_proportion : float

    Returns
    -------
    snr_results : dictionary
            `snr_results['left_snr']` contains a float indicating the results for
            the left region. `snr_results['right_snr']` contains a float
            indicating the results for the right region.
    """
    snr_results = {'left_snr': None, 'right_snr': None}

    regions = assign_regions(unsuppressed_one)
    left_region = regions['left']
    right_region = regions['right']

    left_roi = find_roi(left_region, roi_proportion)
    right_roi = find_roi(right_region, roi_proportion)

    difference_image = unsuppressed_one - unsuppressed_two
    difference_image_left = difference_image.copy()
    difference_image_right = difference_image.copy()

    left_std_dev = difference_image_left[left_roi.astype(bool)].std()
    left_mean = unsuppressed_one[left_roi.astype(bool)].mean()

    right_std_dev = difference_image_right[right_roi.astype(bool)].std()
    right_mean = unsuppressed_one[right_roi.astype(bool)].mean()

    left_snr = left_mean / (sqrt(2)*left_std_dev)
    right_snr = right_mean / (sqrt(2)*right_std_dev)

    snr_results['left_snr'] = left_snr
    snr_results['right_snr'] = right_snr

    return snr_results
