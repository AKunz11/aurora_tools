"""Plot the CO Cameron/UVD emission ratio as a function of latitude."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

def ratio_lat(data, key='All', output_dir='E:/alex_final_figs'):
    """Create a ratio-versus-latitude scatter plot from a detection table."""
    lat=np.asarray(data['latitude'], dtype=float)
    co_ratio=np.abs(np.asarray(data['CO/CO2p'], dtype=float))

    fig, ax = plt.subplots()
    ax.scatter(co_ratio, lat, s=6)
    plt.xlim(0, 200)
    plt.ylim(-90, 90)
    plt.xlabel('CO Cameron / UVD Ratio')
    plt.ylabel(r'Latitude ($^\circ$)')
    plt.title('CO Cameron / UVD Ratio vs Latitude')
    plt.grid(True)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_dir / f'emission_ratio_vs_latitude_{key}.png',
        dpi=300,
        bbox_inches='tight',
    )
    plt.show()
    return
