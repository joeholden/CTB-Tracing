import os
import matplotlib.pyplot as plt

# What is the name of your project? Change the string below
project_name = "Test Project"

# Modify the line below to write a list of animal numbers
animals = [39, 40, 41]

# Where do you want all of this data to save? Edit the path below
working_directory = "C:/Users/joema/PycharmProjects/CTB Tracing"

# Do not edit anything below this
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
project_directory_path = os.path.join(working_directory, project_name)
if not os.path.exists(project_directory_path):
    os.makedirs(project_directory_path)

for animal in animals:
    if not os.path.exists(os.path.join(project_directory_path, str(animal), f"{animal} tif")):
        os.makedirs(os.path.join(project_directory_path, str(animal), f"{animal} tif"))
        os.makedirs(os.path.join(project_directory_path, str(animal), f"{animal} roi"))

# Output a colorbar into the main directory
fig = plt.figure(figsize=(2, 6))
sm = plt.cm.ScalarMappable(cmap='plasma')
sm.set_array([])
cax = fig.add_axes([0.3, 0.1, 0.3, 0.8])  # [left, bottom, width, height]
cbar = fig.colorbar(sm, cax=cax, orientation='vertical')
plt.savefig(os.path.join(project_directory_path, "Plasma Colorbar.png"))
