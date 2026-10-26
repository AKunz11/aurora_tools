"""Plot solar zenith angle counts and a geometric reference distribution."""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def sza_hist(data, key, output_dir='E:/alex_final_figs'):
    """Plot SZA counts for detections at or above 105 degrees.

    The dashed curve represents the expected bin counts for a geometrically
    uniform population over the same SZA range.
    """
    fig,axs=plt.subplots()

    SZA_min = 105
    plot_edges_deg = np.arange(100, 181, 5)

    # observed data should match the allowed range
    sza = data['sza']
    sza = sza[(sza >= SZA_min)]

    sza_counts=len(sza[sza<120])

    counts, _ = np.histogram(sza, bins=plot_edges_deg)
    N = counts.sum()

    print(f'The percent of observations below 120 deg is {sza_counts/N*100}% ({sza_counts}/{N}) ')

    # geometry uses true lower limit in first bin
    geom_edges_deg = plot_edges_deg.astype(float).copy()
    geom_edges_deg[0] = SZA_min
    edges_rad = np.deg2rad(geom_edges_deg)

    geom_w = np.cos(edges_rad[:-1]) - np.cos(edges_rad[1:])
    geom_w /= geom_w.sum()

    expected = geom_w * N

    bin_centers = 0.5 * (plot_edges_deg[:-1] + plot_edges_deg[1:])
    axs.bar(bin_centers, counts, width=np.diff(plot_edges_deg),
            edgecolor='black', align='center', alpha=0.6, label='Detections')
    axs.plot(bin_centers, expected, '--', lw=2, c='black', label='Uniform (geometry)')
    axs.errorbar(bin_centers, counts, yerr=np.sqrt(counts), fmt='none')
    axs.set_xticks(np.arange(100,181,10))
    axs.set_xlabel(r'SZA ($^\circ$)')
    axs.set_ylabel('Counts')
    axs.set_title(f'SZA ({key})')
    axs.legend()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f'sza_{key}.png', dpi=300, bbox_inches='tight')
    plt.show()

    #Bars are actual detections, dashed line is how many you would expect if uniform distribution
    #If bar>line, likely a preference for that data. If less than line, possible avoidance
    return
