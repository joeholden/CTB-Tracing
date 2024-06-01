import pandas as pd
from ctb_trace import loop
from collections import defaultdict
import time
import os
from DIRECTORY_SETUP import project_directory_path, animals
from pathlib import Path

"""
Set up a directory tree where you have unique folders holding rois and images for each animal. For example, for animal
number 36 you would have one folder '36 tif' and '36 roi'.

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

DATA_DIRECTORY = project_directory_path
tif_dirs = [os.path.join(DATA_DIRECTORY, str(num), f"{num} tif") for num in animals]
roi_dirs = [os.path.join(DATA_DIRECTORY, str(num), f"{num} roi") for num in animals]
sides = ['left', 'right']


if __name__ == "__main__":
    zipped = list(zip(tif_dirs, roi_dirs, animals))
    transport_dictionary = defaultdict()

    for i in range(len(zipped)):
        for j in sides:
            print(f"Calculating Transport for: {zipped[i][0].split(os.sep)[-1]}_{j.upper()}")
            transport = loop(tif_directory=zipped[i][0],
                             roi_directory=zipped[i][1],
                             excel_path=os.path.join(Path(zipped[i][0]).parent, "Threshold Values.xlsx"),
                             output_heatmap_name=f'{zipped[i][2]}_{j}',
                             side=j)
            transport_dictionary[f'{zipped[i][2]}_{j}'] = transport

    df = pd.DataFrame(transport_dictionary, index=[0]).T
    df.to_excel(os.path.join(project_directory_path, f'ctb_transport_{time.strftime("%Y%m%d-%H%M%S")}.xlsx'))
