"""Plot temporal and seasonal coverage for filtered detections."""

import matplotlib.pyplot as plt
import datetime as dt

def plot_coverage(data):
    """Plot solar longitude by date and emission ratio by solar longitude.

    Args:
        data: DataFrame containing ``date``, ``solar_longitude``, and
            ``CO/CO2p`` columns.
    """
    #Plot year vs solar longitude
    #Conver date to datetime (e.g. 2016-May-28)
    x = [dt.datetime.strptime(date, '%Y-%b-%d') for date in data['date']]
    y = data['solar_longitude']
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.xlabel('Date')
    plt.ylabel('Solar Longitude ($^\circ$)')
    plt.title('$L_s$ Coverage of Observations')
    plt.grid()
    plt.savefig(f'D:/thesis_images/coverage.png', dpi=300)
    plt.show()

    #Plot solar longitude vs ratio
    x = data['solar_longitude']
    y = 1/data['CO/CO2p']
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, s=10, alpha=0.5)
    plt.ylim(0,0.6) #Can change to higher
    plt.xlabel('Solar Longitude ($^\circ$)')
    plt.ylabel('Ratio')
    plt.title('UVD / CO Cameron Ratio vs Solar Longitude')
    plt.savefig(f'D:/thesis_images/ls_ratio.png', dpi=300)
    plt.show()

    return
