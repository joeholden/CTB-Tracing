import re
import pandas as pd


slide_pattern = r'slide (\d+)?'
slice_pattern = r'slice (\d+)'


def regex_filenames(file_string):
    slide_num = re.search(pattern=slide_pattern, string=file_string).group(1)
    slice_num = re.search(pattern=slice_pattern, string=file_string).group(1)
    return int(slide_num), int(slice_num)


def sort_filenames(list_of_filenames):
    joined_info = []
    for f in list_of_filenames:
        slide_num, slice_num = regex_filenames(f)
        joined_info.append((f, slide_num, slice_num))

    sorted_list = sorted(joined_info, key=lambda x: (x[1], x[2]))
    sorted_list = pd.Series([i[0] for i in sorted_list])
    # sorted_list.to_excel('sorted_filenames.xlsx')
    return sorted_list



