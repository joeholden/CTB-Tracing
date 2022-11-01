import pandas as pd
from ctb_trace import loop
from collections import defaultdict
import time

"""
Set up a directory tree where you have unique folders holding rois and images for each animal. For example, for animal
number 36 you would have one folder '36 tif' and '36 roi'. The names of the folders are not important. 

Change the four lists below to have the directory paths for the SC tifs, rois, animal numbers, and sides. 
Keep the order corresponding between lists. Also change the path to the excel sheet with the thresholds. 

A timestamped excel sheet is output to the home directory with the transport data.

Example:
tif_dirs = ['35 tif', '36 tif']
roi_dirs = ['35 roi', '36 roi']
animals = [35, 36]
sides = ['left', 'right']
threshold_excel_path = 'threshold_values.xlsx'
"""

tif_dirs = ['35 tif']
roi_dirs = ['35 roi']
animals = [35]
sides = ['left', 'right']
threshold_excel_path = 'threshold_values2.xlsx'


if __name__ == "__main__":
    zipped = list(zip(tif_dirs, roi_dirs, animals))
    transport_dictionary = defaultdict()

    for i in range(len(zipped)):
        for j in sides:
            transport = loop(tif_directory=zipped[i][0],
                             roi_directory=zipped[i][1],
                             excel_path= threshold_excel_path,
                             output_heatmap_name=f'{zipped[i][2]}_{j}',
                             side=j)
            transport_dictionary[f'{zipped[i][2]}_{j}'] = transport

    df = pd.DataFrame(transport_dictionary, index=[0]).T
    df.to_excel(f'ctb_transport_{time.strftime("%Y%m%d-%H%M%S")}.xlsx')
