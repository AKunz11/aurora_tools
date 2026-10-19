"""Compare normal and anomalous detections with two-sample K-S tests.

Update ``master_path`` before running this module as a standalone script. The
same quality filters and 12.7 emission-ratio cutoff used by the main workflow
are applied before testing SZA and latitude distributions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp

master_path=r'E:/nightglow/master_cnn.csv' #Huge csv with all data merged
data=pd.read_csv(master_path)
data = data[
    (data['orbit_number'] >= 0) & 
    (data['orbit_number'] < 24600) &
    (data['sza'] >= 105) &
    (data['count'] >= 6) &
    (data['pearson_r_muv'] >= 0.6) &
    (data['color_flag_muv'] == 'green') &
    (data['type']!='NON-DET') &
    (data['type'] != 'NONE') &
    (data['type'] != 'SEP')
]
data = data.drop_duplicates(subset=["nick_number"])

anom_data=data[data['CO/CO2p'] >= 12.7]
norm_data=data[data['CO/CO2p'] < 12.7]

# SZA K-S Test
D, p = ks_2samp(anom_data["sza"].dropna(), norm_data["sza"].dropna())

print('+'*30)
print(f'SZA K-S Test Results:\nGreatest distance D = {D:.3f}\nP-Value p = {p:.3f}')

# Latitude K-S Test
D1, p1 = ks_2samp(anom_data['latitude'].dropna(), norm_data['latitude'].dropna())

print('+'*30)
print(f'Latitude K-S Test Results:\nGreatest distance D = {D1:.3f}\nP-Value p = {p1:.3f}')

# Descriptive bs
print('+'*30)
for name, df in [("Anomalous", anom_data), ("Normal", norm_data)]:
    print(name)
    print(f"SZA median: {df['sza'].median():.1f}")
    print(f"SZA mean:   {df['sza'].mean():.1f}")
    print(f"Latitude median: {df['latitude'].median():.1f}")
    print()

