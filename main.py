"""Run the primary Mars nightglow filtering and visualization workflow.

Configure the selection criteria and local data paths below, then call
``main()`` or run this file as a script. Plotting helpers are opt-in near the
end of ``main()``; the filtered table is always saved as ``filtered_data.csv``.
"""

#Libraries
from turtle import lt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import spiceypy as spice

from sza_hist import *
from map import *
from latitude_hist import *
from ratios import *
from local_time import *
from nightside_dist import *
from coadded import *
from altitude import *
from ratio_lat import *
from coverage import *
from MSO_coords import *

#Matplotlib settings
s=15
plt.rc('font', size=s)
plt.rc('axes', titlesize=s)
plt.rc('axes', labelsize=s)
plt.rc('xtick', labelsize=s)
plt.rc('ytick', labelsize=s)
plt.rc('legend', fontsize=s)
plt.rc('figure', titlesize=s)
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern'], 'size':s})
plt.rc('text', usetex=True)

#Variables
orb_start=100 #usually 2000
orb_stop=24600 #usually 15500
key='All' #All, Anomalous, or Normal
consecutive_check=False #Whether to only include orbits with at least n scans in a row (e.g. 3 or more consecutive orbits that meet the other criteria)
print_stuff=False
isolate_orbits=False
orbit_compare=False
remove_cutoff_bin=False

min_sza=105
n_pix=6
pearson_r=0.6
coUVD=12.7
wl_dim=512 #512 or 219

orb_select=[10384, 10488, 10562, 10563, 10568, 10607, 10617, 10634, 10650,
            10654, 11482, 2512, 2524, 2587, 2730, 3258, 3379, 3389, 3432,
            3439, 3510, 3522, 3614, 3828, 3842, 3849, 3928, 401, 405, 408, 414,
            416, 426, 4403, 4557, 4559, 4567, 4575, 4592, 4624, 4669, 4684, 4702,
            4705, 4717, 6674, 6678, 6679, 6681, 6711, 6753, 6762, 7733, 7760, 7802,
            7838, 7970, 8001, 8018, 8028, 8034, 8057, 8134, 8169, 8319, 8583, 8604,
            8611, 8664, 8676, 8700, 9154, 9369, 9623, 9626] #Adrienne's anomalous orbits

adriennes=pd.DataFrame({'nick_number':
[401.07, 401.08, 405.08, 408.08, 414.07, 416.08, 426.08, 426.09,
2512.03, 2512.04, 2524.01, 2587.04, 2587.06, 2730.07, 3258.02, 3379.11,
3389.12, 3432.12, 3439.08, 3510.12, 3522.10, 3614.07, 3828.07, 3842.09,
3849.10, 3928.11, 4403.04, 4557.10, 4559.04, 4567.11, 4575.09, 4592.09,
4624.08, 4669.12, 4669.09, 4684.11, 4684.10, 4702.04, 4705.07, 4717.11,
6674.03, 6678.08, 6679.05, 6681.08, 6711.07, 6753.10, 6762.07, 7733.10,
7760.02, 7802.09, 7838.03, 7970.03, 8001.07, 8018.07, 8028.01, 8034.04,
8057.05, 8134.11, 8169.01, 8319.01, 8583.03, 8604.07, 8611.01, 8611.02,
8664.01, 8676.05, 8700.08, 9154.06, 9369.14, 9623.04, 9626.07, 10384.10,
10488.02, 10562.09, 10563.13, 10568.08, 10568.09, 10607.09, 10617.11,
10634.04, 10650.04, 10654.04, 11482.04]}) #Adriennes orbits with scans

#print(np.sort(orb_select))
#print("How many orbits does Adrienne have: ", len(orb_select))

#Paths
master_path=r'E:/nightglow/master_cnn.csv' #Huge csv with all data merged
map_img_path=r'bfield_smoothed.npy'
me_and_adrienne_path=r'D:/nightglow_tools/combined_orbits.csv' #csv with all of my detections and all of Adrienne's detections, with classifications of whether each scan is in mine, hers, or both, and whether it's good data or not based on visual inspection csv

#Call function
def main():
    """Filter the master detection table, create selected plots, and save it.

    Returns:
        pandas.DataFrame: Deduplicated detections that pass the configured
        orbit, geometry, signal-quality, and classification filters.
    """
    #Filter data
    data=pd.read_csv(master_path)
    data = data[
        (data['orbit_number'] >= orb_start) & 
        (data['orbit_number'] < orb_stop) &
        (data['sza'] >= min_sza) &
        (data['count'] >= n_pix) &
        (data['pearson_r_muv'] >= pearson_r) &
        (data['color_flag_muv'] == 'green') &
        (data['type']!='NON-DET') &
        (data['type'] != 'NONE') &
        (data['type'] != 'SEP')
    ]
#include (data['type'] != 'NON-DET') above ^^

    lt = data['local_time'] % 24
    data['hours_from_midnight'] = ((lt + 12) % 24) - 12
    if key == 'Anomalous':
        data = data[data['CO/CO2p'] >= coUVD]
    if key == 'Normal':
        data = data[data['CO/CO2p'] < coUVD]

    data=mso_coords(data)
    data = data.drop_duplicates(subset=["nick_number"])

    ######################################################################################
    #Check for consecutive orbits
    if consecutive_check:
        n=2 #how many scans in a row to check for
        orbit_counts = data.groupby('orbit_number')['orbit_number'].transform('count')
        data['consecutive']=orbit_counts >= n
        data = data[data['consecutive'] == True]

        #Print orbits that have duplicates
        duplicate_orbits = data[data.duplicated(subset=['orbit_number'], keep=False)]['orbit_number'].unique()
        print(f"Orbits with at least {n} scans in a row: {duplicate_orbits}")
    ######################################################################################



    ######################################################################################
    #If we want to select Adrienne's orbits
    if isolate_orbits:

        #data = data[data['nick_number'].isin(adriennes)] #Overlap with her nick numbers
        #data = data[~data['nick_number'].isin(adriennes)] #My unique nick numbers
        data = data[data['type']=='NON-DET'] #Visual inspection rejects over ALL nick numbers
        #print(len(data['orbit_number']))
        
        #Restrict to orbit number and nick number columns only, then save that csv
        data=data[['orbit_number', 'nick_number', 'type']]
        data.to_csv('D:/nightglow_tools/visual_inspection.csv', index=False)

        #maka a csv of just adriennes orbits from the table above with orbit number by flooring nick number to get orbit number, then save that csv
        adriennes['orbit_number'] = adriennes['nick_number'].apply(lambda x: int(float(x)))

        df = adriennes[['orbit_number', 'nick_number']]

        df.to_csv('D:/nightglow_tools/adrienne_orbits.csv', index=False)

        #data.to_csv(f'D:/nightglow_tools/adrienne_orbits.csv', index=False)
    ######################################################################################

    if orbit_compare:
        # Read combined orbit classifications
        combined_orbits = pd.read_csv(me_and_adrienne_path)

        combined_orbits['nick_number'] = combined_orbits['nick_number'].astype(str)
        data['nick_number'] = data['nick_number'].astype(str)

        combined_orbits = combined_orbits.drop(columns=['orbit_number'])

        data = pd.merge(
            data,
            combined_orbits,
            on='nick_number',
            how='left'
        )

        # Clean whitespace just in case
        data['mine'] = data['mine'].astype(str).str.strip()
        data['good_data'] = data['good_data'].astype(str).str.strip()

        print(data['mine'].unique())
        print(data['good_data'].unique())

        data = data[
            (data['good_data'] == 'Y') &
            (data['mine'].notna()) &
            (data['orbit_number'] >= 400) &
            (data['orbit_number'] < 15500)
        ]

        data.to_csv(f'D:/nightglow_tools/combined_orbits_with_data.csv', index=False)

    if remove_cutoff_bin:

        target = 1/12.7

        inv_ratio = 1 / data['CO/CO2p']

        bin_edges = np.histogram_bin_edges(inv_ratio, bins=30, range=(-0.1, 0.6))

        bin_idx = np.searchsorted(bin_edges, target) - 1

        bin_lo = bin_edges[bin_idx]
        bin_hi = bin_edges[bin_idx + 1]

        print(f"Removing bin {bin_idx}: [{bin_lo:.4f}, {bin_hi:.4f})")

        # Split dataframe into low/high sides
        data_low  = data[inv_ratio < bin_lo].copy()
        data_high = data[inv_ratio >= bin_hi].copy()

        data=data_low

        print("Low side:", len(data_low))
        print("High side:", len(data_high))


    #Number of detections
    print(f"Number of {key} detections: {len(data)}")
    #Run the plotting functions accordingly:

    #sza_hist(data,key)
    #plot_map(data, map_img_path, key)
    #latitude_hist(data,key,normalized=True, y_max=0.25)
    #plot_local_time(data,key)
    #nightside_dist(data,key,orb_start,orb_stop,label=False)
    #coadd(data,key,wl_dim=wl_dim)
    
    if key == 'All':
        #plot_ratio(data, mode='normal') #mode can be normal or inverse
        #alt_hist(data,n_bins=16)
        #ratio_lat(data)
        #plot_coverage(data) 
        print('Done') #Just in case everything in the if statement is commented out

    if print_stuff:
        #Print largest brightness in data
        print(f"Largest CO brightness in data: {data['CO_radiance'].max()}\n at orbit {data.loc[data['CO_radiance'].idxmax(), 'orbit_number']}")
        print(f"Largest UVD brightness in data: {data['CO2p_radiance'].max()}\n at orbit {data.loc[data['CO2p_radiance'].idxmax(), 'orbit_number']}")

        #Print mean ratio of detections where ratio is greater than 0 (to avoid including non-detections where ratio is set to 0)
        print(f'Mean ratio of detections: {data[data["CO/CO2p"] > 0]["CO/CO2p"].mean()}')

    #Save filtered data
    data.to_csv(f'E:/aurora_tools/filtered_data.csv', index=False, float_format="%.2f")

    return data



if __name__ == "__main__":
    main()
