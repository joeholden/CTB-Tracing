import re
import pandas as pd

"""
This script has the functions which sort your filenames so that they are in order during the tracing script. 
Strips need to be concatenated in the correct anterior to posterior direction. This assumes you have labeled slides
like the following: 'something slide 1 slice 16 something else.extension'
"""
slide_pattern = r'slide (\d+)?'
slice_pattern = r'slice (\d+)'


def regex_filenames(file_string):
    slide_num = re.search(pattern=slide_pattern, string=file_string).group(1)
    slice_num = re.search(pattern=slice_pattern, string=file_string).group(1)
    return int(slide_num), int(slice_num)


def sort_filenames(list_of_filenames):
    """Returns a list of pathnames that are in correct SC slice order as opposed to the random nature of os.walk"""
    joined_info = []
    for f in list_of_filenames:
        slide_num, slice_num = regex_filenames(f)
        joined_info.append((f, slide_num, slice_num))

    sorted_list = sorted(joined_info, key=lambda x: (x[1], x[2]))
    sorted_list = pd.Series([i[0] for i in sorted_list])
    # sorted_list.to_excel('sorted_filenames.xlsx')
    return sorted_list



