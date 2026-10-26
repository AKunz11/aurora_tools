"""Visualize the local-time distribution of nightglow detections."""

import matplotlib.pyplot as plt
from pathlib import Path

def plot_local_time(data, key, output_dir='E:/alex_final_figs'):
    """Plot local time and signed hours from midnight for a detection set.

    Args:
        data: DataFrame containing ``local_time`` and ``hours_from_midnight``.
        key: Human-readable selection label used in plot titles.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig = plt.figure()
    plt.hist(data['local_time'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Distribution of Local Time ({key})')
    plt.xlabel('Local Time')
    fig.savefig(output_dir / f'local_time_{key}.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    fig = plt.figure()
    plt.hist(data['hours_from_midnight'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Hours from midnight ({key})')
    plt.xlabel('Time')
    fig.savefig(
        output_dir / f'hours_from_midnight_{key}.png',
        dpi=300,
        bbox_inches='tight',
    )
    plt.show()
    return
