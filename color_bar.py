import matplotlib.pyplot as plt

fig = plt.figure(figsize=(2, 6))

sm = plt.cm.ScalarMappable(cmap='plasma')
sm.set_array([])

# Create an axis for the colorbar with specific width to make it skinny
cax = fig.add_axes([0.3, 0.1, 0.3, 0.8])  # [left, bottom, width, height]

# Create the colorbar and add it to the figure
cbar = fig.colorbar(sm, cax=cax, orientation='vertical')

plt.show()
