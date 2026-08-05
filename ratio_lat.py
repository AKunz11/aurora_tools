import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def ratio_lat(data):
    lat=np.asarray(data['latitude'], dtype=float)
    co_ratio=np.abs(np.asarray(data['CO/CO2p'], dtype=float))

    plt.scatter(co_ratio, lat, s=6)
    plt.xlim(0, 200)
    plt.ylim(-90, 90)
    plt.xlabel('CO Cameron / UVD Ratio')
    plt.ylabel('Latitude ($^\circ$)')
    plt.title('CO Cameron / UVD Ratio vs Latitude')
    plt.grid(True)
    plt.show()
    return