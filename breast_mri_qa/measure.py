""" This module contains functions used to make the calculations required
    for QA.
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

    Parameters
    ----------
    Returns
    -------
    """
    fat_suppressed = fat_suppressed.copy()
    fat_suppressed_mean_pixel_value = fat_suppressed[roi.astype(bool)].mean()

    water_suppressed = water_suppressed.copy()
    water_suppressed_mean_pixel_value = water_suppressed[roi.astype(bool)].mean()

    suppression_efficiency = 100 * ((fat_suppressed_mean_pixel_value - water_suppressed_mean_pixel_value) / fat_suppressed_mean_pixel_value)
    return suppression_efficiency

def find_roi(region, roi_proportion):
    region_area = regionprops(region)[0].area
    target_roi_area = roi_proportion * region_area
    actual_roi_proportion = 1
    roi = region.copy()
    while actual_roi_proportion > roi_proportion:
        roi = binary_erosion(roi).astype(int)
        actual_roi_proportion = regionprops(roi)[0].area / float(region_area)
    return roi

def assign_regions(image_array):
    img_height = image_array.shape[0]
    img_width = image_array.shape[1]

    otsu_thresh = threshold_otsu(image_array)
    np_mask = image_array > otsu_thresh
    np_mask = np_mask.astype(int)  #Recode booleans as integers
    np_mask[(int(0.75*(img_height))):, :] = 0  #Remove lower parts of phantom from mask
    regions = label(np_mask)
    region_1 = (regions == 1).astype(int)
    region_2 = (regions == 2).astype(int)
    left_region = None
    right_region = None
    regionprops(region_1)[0].centroid[1]
    if (regionprops(region_1)[0].centroid[1] > img_width / 2):  # region centroid (x) > half-way point
        left_region = region_1
        right_region = region_2
    else:
        left_region = region_2
        right_region = region_1

    return {'left': left_region, 'right': right_region}

def get_mid_slice(instance):
    if len(instance) <= 1:
        # Nonsense to get middle slice in this case
        return instance
    pixel_array = instance['PixelArray']
    return pixel_array[int(len(pixel_array) / float(2))]

def fse(fat_suppressed, water_suppressed, roi_proportion=0.8):
    ret_dict = {'left_fse':None, 'right_fse':None}

    regions = assign_regions(fat_suppressed)
    left_region = regions['left']
    right_region = regions['right']

    left_roi = find_roi(left_region, roi_proportion)
    right_roi = find_roi(right_region, roi_proportion)

    #Left Suppression efficiency
    ret_dict['left_fse'] = calculate_efficiency(fat_suppressed, water_suppressed, left_roi)
    ret_dict['right_fse'] = calculate_efficiency(fat_suppressed, water_suppressed, right_roi)

    return ret_dict

def snr(unsuppressed_one, unsuppressed_two, roi_proportion=0.8):
    ret_dict = {'left_snr':None, 'right_snr':None}

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

    ret_dict['left_snr'] = left_snr
    ret_dict['right_snr'] = right_snr

    return ret_dict
