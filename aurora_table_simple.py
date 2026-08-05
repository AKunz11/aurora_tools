import pandas as pd
import numpy as np

master_path=r'D:/nightglow_tables/master.csv' #Huge csv with all data merged

#Variables
orb_start=400 #usually 2000
orb_stop=15500 #usually 15500
key='All' #All, Anomalous, or Normal
consecutive_check=False #Whether to only include orbits with at least n scans in a row (e.g. 3 or more consecutive orbits that meet the other criteria)
print_stuff=False
isolate_orbits=False
orbit_compare=True
remove_cutoff_bin=False

min_sza=105
n_pix=6
pearson_r=0.6
coUVD=12.7
wl_dim=512 #512 or 219

#Stuff
data=pd.read_csv(master_path)
data = data[
    (data['orbit_number'] >= orb_start) & 
    (data['orbit_number'] < orb_stop) &
    (data['sza'] >= min_sza) &
    (data['count'] >= n_pix) &
    (data['pearson_r_muv'] >= pearson_r) &
    (data['color_flag_muv'] == 'green') &
    (data['type']!='NON-DET') &
    (data['type'] != 'NONE')
]

lt = data['local_time'] % 24
data['hours_from_midnight'] = ((lt + 12) % 24) - 12
data["inv_ratio"]=data["CO/CO2p"].apply(lambda x: 1/x if x != 0 else np.nan)


data.to_csv(f'D:/nightglow_tools/nick_data.csv', index=False)