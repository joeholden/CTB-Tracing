import os
from ctb_trace import loop


if __name__ == "__main__":
    sides = ['left', 'right']

    loop(tif_directory='34 tif/',
         roi_directory='34/',
         excel_path='threshold_values2.xlsx',
         output_heatmap_name='34 left',
         side='left')
