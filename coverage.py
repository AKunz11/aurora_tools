"""Plot temporal and seasonal coverage for filtered detections."""

import matplotlib.pyplot as plt
import datetime as dt
from pathlib import Path

def plot_coverage(data, key='All', output_dir='E:/alex_final_figs'):
    """Plot solar longitude by date and emission ratio by solar longitude.

    Args:
        data: DataFrame containing ``date``, ``solar_longitude``, and
            ``CO/CO2p`` columns.
    """
    #Plot year vs solar longitude
    #Conver date to datetime (e.g. 2016-May-28)
    x = [dt.datetime.strptime(date, '%Y-%b-%d') for date in data['date']]
    y = data['solar_longitude']
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.xlabel('Date')
    plt.ylabel(r'Solar Longitude ($^\circ$)')
    plt.title('$L_s$ Coverage of Observations')
    plt.grid()
    fig.savefig(
        output_dir / f'date_vs_solar_longitude_{key}.png',
        dpi=300,
        bbox_inches='tight',
    )
    plt.show()

    #Plot solar longitude vs ratio
    x = data['solar_longitude']
    y = 1/data['CO/CO2p']
    fig = plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.ylim(0,0.6) #Can change to higher
    plt.xlabel(r'Solar Longitude ($^\circ$)')
    plt.ylabel('Ratio')
    plt.title('UVD / CO Cameron Ratio vs Solar Longitude')
    fig.savefig(
        output_dir / f'solar_longitude_vs_emission_ratio_{key}.png',
        dpi=300,
        bbox_inches='tight',
    )
    plt.show()

    return
