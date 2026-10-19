import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def latitude_hist(data, key, normalized=False, y_max=None,
                  output_dir='D:/thesis_images'):
    """Plot a latitude histogram against the area-weighted geometry reference.

    Set ``normalized=True`` for a fraction-of-detections plot.  Use the same
    ``y_max`` value for the normal and anomalous calls so their axes match.
    """
    latitudes = data['latitude'].dropna().to_numpy()
    if latitudes.size == 0:
        raise ValueError("No finite latitude values are available to plot.")

    lat_edges_deg = np.arange(-90, 91, 20)
    widths = np.diff(lat_edges_deg)
    bin_centers = 0.5 * (lat_edges_deg[:-1] + lat_edges_deg[1:])

    # Equal surface area is proportional to sin(latitude), not latitude itself.
    edge_radians = np.deg2rad(lat_edges_deg)
    geometry_fraction = np.diff(np.sin(edge_radians))
    geometry_fraction /= geometry_fraction.sum()

    counts, _ = np.histogram(latitudes, bins=lat_edges_deg)
    n_detections = counts.sum()

    if normalized:
        values = counts / n_detections
        expected = geometry_fraction
        errors = np.sqrt(counts) / n_detections
        y_label = 'Fraction of detections'
        suffix = '_normalized'
    else:
        values = counts
        expected = geometry_fraction * n_detections
        errors = np.sqrt(counts)
        y_label = 'Detections'
        suffix = ''

    fig, ax = plt.subplots()
    ax.bar(
        bin_centers, values, width=widths, edgecolor='black', align='center',
        alpha=0.6, label='Detections'
    )
    ax.plot(
        bin_centers, expected, '--', lw=2, c='black',
        label='Uniform surface-area expectation'
    )
    ax.errorbar(bin_centers, values, yerr=errors, fmt='none', c='black', capsize=2)

    ax.set_xlabel(r'Latitude ($^\circ$)')
    ax.set_ylabel(y_label)
    ax.set_title(f'Latitude ({key})')
    ax.set_xticks(np.arange(-90, 91, 20))
    ax.set_xlim(-90, 90)
    ax.set_ylim(bottom=0, top=y_max)
    ax.legend()
    fig.tight_layout()

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    fig.savefig(Path(output_dir) / f'lat_{key}{suffix}.png', dpi=300)
    plt.show()
    return fig, ax