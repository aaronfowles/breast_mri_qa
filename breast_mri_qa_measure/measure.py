import os
import dicom
import numpy as np

from math import sqrt, ceil

from skimage.filters import threshold_otsu

from skimage.measure import label, regionprops

from skimage.morphology import binary_erosion, binary_dilation

def calc_fse(fat_suppressed, water_suppressed, roi_proportion=0.8):
    ret_dict = {'left_fse':None,'right_fse':None}

    fat_suppressed_img_height = fat_suppressed.shape[0]
    fat_suppressed_img_width = fat_suppressed.shape[1]

    # Threshold regions
    otsu_thresh = threshold_otsu(fat_suppressed)
    np_mask = fat_suppressed > otsu_thresh
    np_mask = np_mask.astype(int) #Recode booleans as integers
    np_mask[(3*(fat_suppressed_img_height / 4)):,:] = 0 #Remove lower parts of phantom from mask
    regions = label(np_mask)
    region_1 = (regions == 1).astype(int)
    region_2 = (regions == 2).astype(int)
    left_region = None
    right_region = None
    regionprops(region_1)[0].centroid[1]
    if (regionprops(region_1)[0].centroid[1] > fat_suppressed_img_width / 2): # region centroid (x) > half-way point
        left_region = region_1
        right_region = region_2
    else:
        left_region = region_2
        right_region = region_1

    # Locations are specified as tuples in (y,x) top-left is (0,0)
    left_center = regionprops(left_region)[0].centroid
    right_center = regionprops(right_region)[0].centroid

    left_region_area = regionprops(left_region)[0].area
    right_region_area = regionprops(right_region)[0].area

    left_target_roi_area = roi_proportion * left_region_area
    actual_left_roi_proportion = 1
    left_roi = left_region.copy()
    while actual_left_roi_proportion > roi_proportion:
        left_roi = binary_erosion(left_roi).astype(int)
        actual_left_roi_proportion = regionprops(left_roi)[0].area / float(left_region_area)

    right_target_roi_area = roi_proportion * right_region_area
    actual_right_roi_proportion = 1
    right_roi = right_region.copy()
    while actual_right_roi_proportion > roi_proportion:
        right_roi = binary_erosion(right_roi).astype(int)
        actual_right_roi_proportion = regionprops(right_roi)[0].area / float(right_region_area)

    #Left Suppression efficiency
    fat_suppressed_left = fat_suppressed.copy()
    fat_suppressed_left[~left_roi.astype(bool)] = 0
    left_fat_suppressed_mean_pixel_value = fat_suppressed_left.mean()
    water_suppressed_left = water_suppressed.copy()
    water_suppressed_left[~left_roi.astype(bool)] = 0
    left_water_suppressed_mean_pixel_value = water_suppressed_left.mean()
    left_suppression_efficiency = 100 * ((left_fat_suppressed_mean_pixel_value - left_water_suppressed_mean_pixel_value) / left_fat_suppressed_mean_pixel_value)

    #Right Suppression efficiency
    fat_suppressed_right = fat_suppressed.copy()
    fat_suppressed_right[~right_roi.astype(bool)] = 0
    right_fat_suppressed_mean_pixel_value = fat_suppressed_right.mean()
    water_suppressed_right = water_suppressed.copy()
    water_suppressed_right[~right_roi.astype(bool)] = 0
    right_water_suppressed_mean_pixel_value = water_suppressed_right.mean()
    right_suppression_efficiency = 100 * ((right_fat_suppressed_mean_pixel_value - right_water_suppressed_mean_pixel_value) / right_fat_suppressed_mean_pixel_value)

    ret_dict['left_fse'] = left_suppression_efficiency
    ret_dict['right_fse'] = right_suppression_efficiency

    return ret_dict

def calc_snr(unsuppressed_one,unsuppressed_two,roi_proportion=0.8):
    ret_dict = {'left_snr':None,'right_snr':None}

    unsuppressed_img_height = unsuppressed_one.shape[0]
    unsuppressed_img_width = unsuppressed_two.shape[1]

    # Threshold regions
    otsu_thresh = threshold_otsu(unsuppressed_one)
    np_mask = unsuppressed_one > otsu_thresh
    np_mask = np_mask.astype(int) #Recode booleans as integers
    np_mask[(3*(unsuppressed_img_height / 4)):,:] = 0 #Remove lower parts of phantom from mask
    regions = label(np_mask)
    region_1 = (regions == 1).astype(int)
    region_2 = (regions == 2).astype(int)
    left_region = None
    right_region = None
    regionprops(region_1)[0].centroid[1]
    if (regionprops(region_1)[0].centroid[1] > unsuppressed_img_width / 2): # region centroid (x) > half-way point
        left_region = region_1
        right_region = region_2
    else:
        left_region = region_2
        right_region = region_1

    # Locations are specified as tuples in (y,x) top-left is (0,0)
    left_center = regionprops(left_region)[0].centroid
    right_center = regionprops(right_region)[0].centroid

    left_region_area = regionprops(left_region)[0].area
    right_region_area = regionprops(right_region)[0].area

    left_target_roi_area = roi_proportion * left_region_area
    actual_left_roi_proportion = 1
    left_roi = left_region.copy()
    while actual_left_roi_proportion > roi_proportion:
        left_roi = binary_erosion(left_roi).astype(int)
        actual_left_roi_proportion = regionprops(left_roi)[0].area / float(left_region_area)

    right_target_roi_area = roi_proportion * right_region_area
    actual_right_roi_proportion = 1
    right_roi = right_region.copy()
    while actual_right_roi_proportion > roi_proportion:
        right_roi = binary_erosion(right_roi).astype(int)
        actual_right_roi_proportion = regionprops(right_roi)[0].area / float(right_region_area)

    difference_image = unsuppressed_one - unsuppressed_two

    difference_image_left = difference_image.copy()
    difference_image_left[~left_roi.astype(bool)] = 0

    difference_image_right = difference_image.copy()
    difference_image_right[~right_roi.astype(bool)] = 0

    left_std_dev = difference_image_left.std()
    left_mean = difference_image_left.mean()

    right_std_dev = difference_image_right.std()
    right_mean = difference_image_right.mean()

    left_snr = left_mean / (sqrt(2)*left_std_dev)
    right_snr = right_mean / (sqrt(2)*right_std_dev)

    ret_dict['left_snr'] = left_snr
    ret_dict['right_snr'] = right_snr

    return ret_dict
