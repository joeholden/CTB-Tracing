import cv2
import nd2
import matplotlib as mpl
import matplotlib.pyplot as plt
import roifile
import numpy as np
import statistics as stats
from collections import defaultdict
import math
import os
from skimage import io
import pandas as pd
from pathlib import Path
import sys


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


def single_section_intensity_strip(nd2_path, strip_width, sc_roi_path, background_roi_path, resolution,
                                   background_information, side, bg='manual'):
    """Returns a vertical strip image where the top corresponds to the medial SC and the bottom to the lateral SC.
    Intensities along a horizontal strip in this image are the average intensity along a 6um-wide
    dorsal-ventral strip of the original SC image. Additionally, a tuple is returned with the total number of
    dorsal-ventral slices in the image as well as the number of those slices that have CTB density >=70%.
    Parameters:
    'nd2_path':
    'strip_width': integer in microns
    'sc_roi_path':
    'background_roi_path':
    'resolution': decimal px/um
    'background_information':  list where the first element is the path to the excel file, the second is the sc
        image column name, and the third is the background value column name
    'side' should be either 'left' or 'right' and controls the heatmap display orientation"""

    image = nd2.imread(nd2_path).astype(np.uint16)
    sc_pixels = get_roi_pixels(sc_roi_path)

    # Get a background fluorescence value
    if bg != 'manual':
        background_pixels = get_roi_pixels(background_roi_path)
        background_intensities = []
        for pixel in background_pixels:
            intensity = image[pixel[1], pixel[0]]
            background_intensities.append(intensity)
        background = stats.mean(background_intensities)  # plus 5 * stats.stdev(background_intensities)
        # The background defined by the periaqueductal grey is too low
        background = 1.65 * background
    else:
        zipped_bg = read_background(background_information)
        image_name = Path(nd2_path).stem

        for index, val in enumerate(zipped_bg):
            if str(val[0]) == image_name:
                background = val[1]
        try:
            background
        except NameError:
            print('Background was not defined')
            sys.exit(1)

    # For each ~6um x-distance along the ROI range bounds, find the pixel intensity at each y position (vertical strip)
    # Find the number of those pixels that are above background level (CTB density). Save as a decimal 0-1. 
    strips = defaultdict(list)
    strip_width_dv = math.ceil(6 * resolution)
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
        above_bg = [1 if i > background else 0 for i in intensity_array]
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
    # Medial on Top for Left SC. Check for Right?
    transposed = medial_lateral_sc_densities.transpose(1, 0)
    if side.lower() == 'left':
        transposed = cv2.flip(transposed, 0)
    return transposed, (num_slices, num_slices_above_70_ctb)


def loop(nd2_directory, roi_directory, strip_width, resolution, background_info, side):
    """
    Loops through all the SC images, gets CTB transport value, writes image, and stdout the transport percent.

    :param nd2_directory: full path to directory
    :param roi_directory: full path to directory
    :param strip_width: integer in microns
    :param resolution: float in px/um
    :param side: left or right, case insensitive
    :param background_info: list where the first element is the path to the excel file, the second is the sc
        image column name, and the third is the background value column name

    """
    paths_to_images = []
    for root, dirs, files in os.walk(nd2_directory):
        for file in files:
            paths_to_images.append(os.path.join(root, file))

    num_images = len(paths_to_images)
    strips = []
    total_dorsal_ventral_slices = 0
    total_dorsal_ventral_slices_above_70 = 0
    for i in range(1, num_images):  # TODO: numpages +1 doesnt work?
        im, (num_slices, num_slices_above_70_ctb) = single_section_intensity_strip(
            nd2_path=os.path.join(nd2_directory, f'{i}.nd2'), strip_width=strip_width,
            sc_roi_path=os.path.join(roi_directory, str(i) + '.roi'),
            background_roi_path=os.path.join(roi_directory, str(2 * 1) + '.roi'),
            resolution=resolution, background_information=background_info, side=side)
        strips.append(im)
        total_dorsal_ventral_slices += num_slices
        total_dorsal_ventral_slices_above_70 += num_slices_above_70_ctb
        # cv2.imwrite(f'strips/strip{i}.png', im)

    transport = round((total_dorsal_ventral_slices_above_70 / total_dorsal_ventral_slices) * 100, 1)
    print('Percent Intact Transport: ', transport, '%')
    padded_images = []
    max_strip_length = max([i.shape[0] for i in strips])
    count = 1
    for image in strips:
        left_pad = int(math.floor((max_strip_length - image.shape[0]) / 2))
        right_pad = max_strip_length - image.shape[0] - left_pad
        # if you pad RGB, add another (0,0) to the end of the second term below
        padded = np.pad(image, [(left_pad, right_pad), (0, 0)], 'constant')
        padded_images.append(padded)

    new_image = cv2.hconcat(padded_images).astype(np.uint8)

    plt.imsave('plasma_colormap.png', new_image, cmap='plasma')
    io.imsave(f'8_bit_no_map.png', new_image)
    # TODO: Output transport to excel file
    # TODO: Get proper filenames for heatmaps

    # Make a mask of the heatmap so you can remove background on the final colormapped image without touching data
    mask_strips = [np.full(i.shape, 255) for i in strips]
    mask_padded_images = []
    for image in mask_strips:
        left_pad = int(math.floor((max_strip_length - image.shape[0]) / 2))
        right_pad = max_strip_length - image.shape[0] - left_pad
        # if you pad RGB, add another (0,0) to the end of the second term below
        padded = np.pad(image, [(left_pad, right_pad), (0, 0)], 'constant')
        mask_padded_images.append(padded)
    mask = cv2.hconcat(mask_padded_images).astype(np.uint8)
    io.imsave(f'mask.png', mask)

    return transport


def read_background(background_information):
    """This function reads an excel file containing manual determined 16-bit background intensities
    for each SC slice and returns a zipped list with the image name and background. The parameter background
    should be a list where the first element is the path to the excel file, the second is the sc image column name,
    and the third is the background value column name"""
    [excel_path, sc_image_header, bg_header] = background_information
    df = pd.read_excel(excel_path)
    image_names = df[sc_image_header]
    bg_values = df[bg_header]
    zipped = list(zip(image_names, bg_values))
    return zipped


def clean_heatmap(mask, heatmap, background_color_bgr):
    """Removes background for heatmap. It is generated in b/w then a colormap applied.
    This colors the background with the colormap colors. This function fixes that"""
    m = cv2.imread(mask, cv2.IMREAD_UNCHANGED)
    heatmap = cv2.imread(heatmap)
    for x in range(m.shape[1]):
        for y in range(m.shape[0]):
            if m[y, x] == 0:
                heatmap[y, x] = background_color_bgr
    cv2.imwrite('j.png', heatmap)


# loop(nd2_directory='34 nd2',
#      roi_directory='RoiSet', strip_width=5,
#      resolution=0.6154, background_info=['34.xlsx', 'image', 'bg'], side='right')

clean_heatmap('mask.png', 'left.png', [0, 0, 0])

# TODO: Right now all filenames are read in as numbers. This has to be generalized. Set up naming convention
# TODO: ROI filenames are also numbers
# TODO: For the final image remove background blue color with black. Mask the SC region
