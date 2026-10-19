"""Visualize the local-time distribution of nightglow detections."""

import matplotlib.pyplot as plt

def plot_local_time(data,key):
    """Plot local time and signed hours from midnight for a detection set.

    Args:
        data: DataFrame containing ``local_time`` and ``hours_from_midnight``.
        key: Human-readable selection label used in plot titles.
    """
    plt.figure()
    plt.hist(data['local_time'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Distribution of Local Time ({key})')
    plt.xlabel('Local Time')
    plt.show()
    
    plt.figure()
    plt.hist(data['hours_from_midnight'],bins=20,edgecolor='black',alpha=.6)
    plt.title(f'Hours from midnight ({key})')
    plt.xlabel('Time')
    plt.show()
    return
