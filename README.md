# CTB Tracing Superior Colliculus
This script is meant to be a replacement for an Image Pro macro to quantify in tact CTB transport to the superior colliculus. The Image Pro macro is no longer maintained and the license for Image Pro is $5k.
Eventually, this is meant to become a more automated repository. Currently, significant manual input is needed in ImageJ tracing ROIs. 

1. Using ImageJ, Trace ROI of superficial layers of SC using the polygon tool. Trace .nd2 files. If you trace other formats, alter the ctb_trace.py file line 150 where the roi_path is defined in the function loop- it assumes .nd2. 
2. Add ROIs to the manager using the SaveROI macro. Start with the Left side and then the Right.
3. Take 16 bit .nd2 files from the Nikon Eclipse microscope and convert them to 8 bit TIF files using Batch ND2_TIF8 macro.
4. Determine background level to substract using the script get_thresholds.py. This measures 8 bit thresholds. 
5. If your images are not named using the pattern 'something slide X slice Y something.extension', Change regex_sort.py to meet your needs. Files need to be sorted so ctb_trace.py knows the order of sections for heatmap construction. 
6. Run main.py to output heatmaps and transport data to excel sheet. 
