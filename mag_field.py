import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_map(map_img_dir):
    mag_cmap = plt.get_cmap('Blues')
    mag_cmap.set_bad((1,1,1))

    map_img = np.load(map_img_dir, allow_pickle=False)

    fig,axs=plt.subplots()
    mag_topo = plt.imshow(map_img, cmap=mag_cmap, norm=colors.LogNorm(vmin=0.001, vmax=1), origin='lower', extent=[0, 360, -90, 90])
    divider = make_axes_locatable(axs)

    cax = divider.append_axes("right", size="5%", pad=0.2, aspect=10)
    cbar_map = fig.colorbar(mag_topo, cax=cax)
    tick_locations = [.001, .01, .1, 1]
    cbar_map.set_ticks(tick_locations)
    cbar_map.set_ticklabels([str(tick) for tick in tick_locations])
    cbar_map.set_label('Magnetic Topology')
    cbar_map.ax.yaxis.set_label_position('left') 

    axs.set_xlabel('Longitude ($^\circ$)')
    axs.set_ylabel('Latitude ($^\circ$)')
    axs.set_title(f'Mars Crustal Magnetic Field Map')
    plt.show()
    return

plot_map(r'D:/bfield_smoothed.npy')