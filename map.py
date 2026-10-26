"""Plot detection locations over a Mars crustal magnetic-field map."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

def plot_map(data, map_img_dir, key, output_dir='E:/alex_final_figs'):
    """Overlay orbit-colored detections on a magnetic-field background.

    Args:
        data: DataFrame with ``longitude``, ``latitude``, and ``orbit_number``.
        map_img_dir: Path to the NumPy magnetic-field array.
        key: Human-readable selection label used in the title.
    """
    mag_cmap = plt.get_cmap('Greys')
    mag_cmap.set_bad((1,1,1))

    map_img = np.load(map_img_dir, allow_pickle=False)

    orbit_vals=np.asarray(data['orbit_number'])
    norm_orbit=colors.Normalize(vmin=np.min(orbit_vals),vmax=np.max(orbit_vals))

    fig,axs=plt.subplots()
    mag_topo = plt.imshow(map_img, cmap=mag_cmap, norm=colors.LogNorm(vmin=0.001, vmax=1), origin='lower', extent=[0, 360, -90, 90])
    divider = make_axes_locatable(axs)
    sc=axs.scatter(data['longitude'],data['latitude'],s=3,c=orbit_vals,norm=norm_orbit,cmap='gist_rainbow')

    cax = divider.append_axes("right", size="5%", pad=0.2, aspect=10)
    cbar_map = fig.colorbar(mag_topo, cax=cax)
    tick_locations = [.001, .01, .1, 1]
    cbar_map.set_ticks(tick_locations)
    cbar_map.set_ticklabels([str(tick) for tick in tick_locations])
    cbar_map.set_label('Magnetic Topology')
    cbar_map.ax.yaxis.set_label_position('left') 

    cax_orbit = divider.append_axes("bottom", size="5%", pad=0.6)
    cbar_orbit = fig.colorbar(sc, cax=cax_orbit, orientation='horizontal')
    cbar_orbit.set_label('Orbit number')

    axs.set_xlabel(r'Longitude ($^\circ$)')
    axs.set_ylabel(r'Latitude ($^\circ$)')
    axs.set_title(f'Location of {key} Detections (n={len(data)})')
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f'map_{key}.png', dpi=300, bbox_inches='tight')
    plt.show()
    return
