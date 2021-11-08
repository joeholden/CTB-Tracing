import pandas as pd
import os
import csv

#
# # for each file in directory /sc_excel_files:
# # run the conversion sequence below
# #
#
# # converts xlsx to csv for a single file.
# # put in a place holder get the string name for each file and replace that
# df = pd.read_excel("./sc_excel_files/test_file.xlsx")
# left_intensity = pd.DataFrame()
# right_intensity = pd.DataFrame()
# sc_areas = pd.DataFrame()
# # copies the column from the sc intensity measurements excel sheet
# intensity_measurements_to_copy = df["Norm. Int."]
#
# # makes a new column in left_intensity that is the column from the intensity measurements sheet
# left_intensity['next_column'] = intensity_measurements_to_copy
#
# # grabs the column from the intensity measurements sheet containing the area information. Assigns the two new variables
# area_list = df['Total Stained Area (square mm)'][0:7]
# total_stained_area = area_list[0]
# total_area = area_list[3]
# # place these variables in a list or dictionary
#
# # returns a list containing the names of the entries in the directory given by the path. Arbitrary order
# file_list = os.listdir('./sc_excel_files')
# print(file_list)


# The key will be to do all the left first then all the right
# separate these files out into two folders


# loops through files in the directory and adds the intensity measurements column to left_intensity

# counter = 1
# left_intensity = pd.DataFrame()
# file_list = os.listdir('./sc_excel_files/raw')
# list.sort() will put it in alphabetical order but will put number say 17 before 3 because it doesnt recognize the unit

# for f in file_list:
#     df = pd.read_excel(f"./sc_excel_files/raw/{f}")
#     intensity_measurements_to_copy = df["Norm. Int."]
#     left_intensity[f'{counter}'] = intensity_measurements_to_copy
#     counter += 1
# left_intensity.to_excel('./test_jj.xlsx')
#



# checks the length of the animal number.
# Will need to know this to determine the slice number from a position in the string


file_list = os.listdir('./sc_excel_files/raw')
counter = 0
single_digit_slices = []
double_digit_slices =[]

for file in file_list:

    # print(file_list[file_list.index(file)])
    x = file_list[file_list.index(file)]
    for i in x:
        if i != '_':
            counter += 1
        else:
            break
    # print(counter)

    if counter == 2:
        n1 = file_list[file_list.index(file)][16]
        n2 = file_list[file_list.index(file)][17]
        if n2 == '_':
            is_single_digit_slice = True
            single_digit_slices.append(file)
        else:
            is_single_digit_slice = False
            double_digit_slices.append(file)


    counter = 0

ordered_list = single_digit_slices + double_digit_slices
print(ordered_list)