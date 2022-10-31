import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt
import roifile
import numpy as np
from collections import defaultdict
import math
import os
from skimage import io
import pandas as pd
import sys
from regex_sort import sort_filenames


def get_roi_pixels(roi_path):
    """Returns a list of pixel points that lie within a polygon ROI. Be sure to reference these points
    in opencv as reversed. They are saved (i, j) but referencing a pixel in opencv would be image[j, i]"""
    roi = roifile.ImagejRoi.fromfile(roi_path)
    # rectangle bounds
    x_bounds = (min([i[0] for i in roi.coordinates()]), max([i[0] for i in roi.coordinates()]))
    y_bounds = (min([i[1] for i in roi.coordinates()]), max([i[1] for i in roi.coordinates()]))

    px_inside = []
    path = mpl.path.Path(roi.coordinates())
    for i in range(x_bounds[0], x_bounds[1]):
        for j in range(y_bounds[0], y_bounds[1]):
            inside_test = path.contains_point((i, j), transform=None, radius=0.0)
            if inside_test:
                px_inside.append((i, j))
    return px_inside


def single_section_intensity_strip(tif_path, sc_roi_path, excel_path, side, strip_width=5, resolution=0.6154):
    """Returns a vertical strip image where the top corresponds to the medial SC and the bottom to the lateral SC.
    Intensities along a horizontal strip in this image are the average intensity along a 6um-wide
    dorsal-ventral strip of the original SC image. Additionally, a tuple is returned with the total number of
    dorsal-ventral slices in the image as well as the number of those slices that have CTB density >=70%.

    This code is written to deal with 8 bit TIF images. ND2 are 16 bit and there are conversion issues with brightness
    if you load the full 16 bit image and try to display it.

    Medial SC on top of image, Lateral SC on bottom, A-P depends on how you number/image your slides

    Parameters:
    :param tif_path:
    :param sc_roi_path:
    :param excel_path:
    :param strip_width: integer value for the width of each vertical strip of the final heatmap corresponding
           to a single section.
    :param resolution: decimal px/um. Default resolution is for 4x Nikon scope
    :param side: should be either 'left' or 'right' and controls the heatmap display orientation"""

    image = cv2.imread(tif_path)
    sc_pixels = get_roi_pixels(sc_roi_path)

    # Get a background fluorescence value
    zipped_bg = read_background(excel_path, side)
    background = [i for i in zipped_bg if i[0] == tif_path.split('/')[1]][0][1]

    # For each ~6um x-distance along the SC ROI range bounds, find the pixel intensity at each y position
    # (vertical strip). Find the number of those pixels that are above background level (CTB density).
    # Save as a decimal 0-1.

    strips = defaultdict(list)
    strip_width_dv = math.ceil(6 * resolution)  # dv dorsal ventral strip width in raw SC image
    bins = []  # include left edges of pixel bins
    x_vals = [i[0] for i in sc_pixels]  # Get x-values of all SC pixels
    min_x = min(x_vals)
    max_x = max(x_vals)
    for i in range(min_x, max_x + 1, strip_width_dv):
        bins.append(i)
    bin_identity_per_x_val = np.digitize(x_vals, bins)  # Assigns a bin number to each value in x_vals. Bins start at 1
    bin_mappings = sorted(set(zip(bin_identity_per_x_val, x_vals)))  # (bin number, pixel_x_value)

    # Get the index of each pixel and then reference back to bin mappings for the bin number
    sorted_x_vals = [i[1] for i in bin_mappings]
    for px in sc_pixels:
        bin_number = bin_mappings[sorted_x_vals.index(px[0])][0]
        dictionary_index = min_x + (bin_number - 1) * strip_width_dv
        strips[dictionary_index].append(image[px[1], px[0]])

    ctb_density = defaultdict()  # bin_key: (CTB density as fraction of pixels above background, Greater 70% Boolean)
    for key in strips.keys():
        intensity_array = strips[key]
        above_bg = [1 if i[1] > background else 0 for i in intensity_array]
        density = sum(above_bg) / len(intensity_array)
        ctb_density[key] = (density, density >= 0.7)

    # create an array of the CTB density values along the medial-lateral axis of the SC
    medial_lateral_sc_densities = np.array([i[1][0] for i in ctb_density.items()])  # 1D array with density values (0-1)
    medial_lateral_sc_densities = [round(i, 1) for i in 255 * medial_lateral_sc_densities]  # map to 8 bit pixel value
    medial_lateral_sc_densities = [255 if i == 256 else i for i in medial_lateral_sc_densities]  # max val is 255

    # Track transport along medial-lateral axis.
    # Want the total number of slices and the number of slices that have CTB density >=70%.
    above_70_ctb = np.array([i[1][1] for i in ctb_density.items()])
    num_slices = len(above_70_ctb)
    num_slices_above_70_ctb = np.count_nonzero(above_70_ctb)

    # take the array and make it a matrix so the final image isn't super skinny. Tile it based on strip_width input.
    medial_lateral_sc_densities = np.tile(medial_lateral_sc_densities, (strip_width, 1))

    # Transpose so correct orientation of vertical strip is acquired.
    # Medial on Top, Lateral on the Bottom.
    transposed = medial_lateral_sc_densities.transpose(1, 0)
    if side.lower() == 'left':
        transposed = cv2.flip(transposed, 0)
    return transposed, (num_slices, num_slices_above_70_ctb)


def loop(tif_directory, roi_directory, excel_path, side, output_heatmap_name, strip_width=5, resolution=0.6154):
    """
    Loops through all the SC images for a single animal, gets CTB transport value, writes image, and stdout the
    transport percent. Also returns the transport percentage. SC images are 8 bit TIFs and SC rois come from .nd2
    (so end in .nd2.roi). Function returns animal CTB transport.

    :param tif_directory: full path to directory
    :param roi_directory: full path to directory
    :param excel_path: path to excel sheet with background values. This is generated from get_thresholds.py
    :param side: left or right, case insensitive
    :param output_heatmap_name: how you want the heatmap file to be named. Don't include extension.
    :param strip_width: integer value for the width of each vertical strip of the final heatmap corresponding
           to a single section.
    :param resolution: decimal px/um. Default resolution is for 4x Nikon scope

    """
    # Get the paths to all the images in a single animal SC
    paths_to_images = []
    for root, dirs, files in os.walk(tif_directory):
        for file in files:
            if file != '.DS_Store':  # weird mac hidden file
                paths_to_images.append(os.path.join(root, file))
    paths_to_images = sort_filenames(paths_to_images)  # sorts filenames using regex so they are in the correct order

    num_images = len(paths_to_images)
    strips = []

    # Keep track of total number of slices and total number of slices that are above 70% transport. This is done per
    # animal. The single_section_intensity_strip function returns the data for all the strips in the image. The below
    # loop aggregates this for all sections in the animal.
    total_dorsal_ventral_slices = 0
    total_dorsal_ventral_slices_above_70 = 0
    for i in range(num_images):
        tif_path = paths_to_images[i]
        roi_path = os.path.join(roi_directory, f'{side.title()[0]}_{tif_path.split("/")[-1].strip(".tif")}.nd2.roi')

        try:
            im, (num_slices, num_slices_above_70_ctb) = single_section_intensity_strip(
                tif_path=tif_path, strip_width=strip_width, sc_roi_path=roi_path, resolution=resolution,
                excel_path=excel_path, side=side)
        except FileNotFoundError as e:
            # This is if there is a mismatch in the number of ROI files and Images.
            print(e)

        strips.append(im)
        total_dorsal_ventral_slices += num_slices
        total_dorsal_ventral_slices_above_70 += num_slices_above_70_ctb

    transport = round((total_dorsal_ventral_slices_above_70 / total_dorsal_ventral_slices) * 100, 1)
    print('Percent Intact Transport: ', transport, '%')

    # Create the heatmap. Each strip needs to be padded so that the middle of the strip is the middle of the heatmap.
    # Makes the final image more circular than V shaped.
    padded_images = []
    max_strip_length = max([i.shape[0] for i in strips])
    count = 1
    for image in strips:
        left_pad = int(math.floor((max_strip_length - image.shape[0]) / 2))
        right_pad = max_strip_length - image.shape[0] - left_pad
        # if you pad RGB, add another (0,0) to the end of the second term below
        padded = np.pad(image, [(left_pad, right_pad), (0, 0)], 'constant')
        padded_images.append(padded)

    # Concatenate padded strips together into heatmap. Save with plasma CMAP.
    heatmap = cv2.hconcat(padded_images).astype(np.uint8)
    plt.imsave(f'{output_heatmap_name}.png', heatmap, cmap='plasma')

    # Make a mask of the heatmap so you can remove background on the final color-mapped image without touching data
    mask_strips = [np.full(i.shape, 255) for i in strips]
    mask_padded_images = []
    for image in mask_strips:
        left_pad = int(math.floor((max_strip_length - image.shape[0]) / 2))
        right_pad = max_strip_length - image.shape[0] - left_pad
        # if you pad RGB, add another (0,0) to the end of the second term below
        padded = np.pad(image, [(left_pad, right_pad), (0, 0)], 'constant')
        mask_padded_images.append(padded)
    mask = cv2.hconcat(mask_padded_images).astype(np.uint8)
    io.imsave(f'{output_heatmap_name}_mask.png', mask)

    # Remove background in heatmap
    heatmap = cv2.imread(f'{output_heatmap_name}.png')
    for x in range(mask.shape[1]):
        for y in range(mask.shape[0]):
            if mask[y, x] == 0:
                heatmap[y, x] = (0, 0, 0)
    cv2.imwrite(f'{output_heatmap_name}.png', heatmap)
    os.remove(f'{output_heatmap_name}_mask.png')

    return transport


def read_background(excel_path, side):
    """This function reads an excel file containing manual determined 16-bit background intensities
    for each SC slice and returns a zipped list with the image name and background. The parameter background
    should be a list where the first element is the path to the excel file, the second is the sc image column name,
    and the third is the background value column name"""
    df = pd.read_excel(excel_path)
    image_names = df['Filename']
    if side.lower() == 'left':
        bg_values = df['Left BG']
    elif side.lower() == 'right':
        bg_values = df['Right BG']
    else:
        print('Incorrect Side Listed for Background')
        sys.exit(1)
    zipped = list(zip(image_names, bg_values))
    return zipped



