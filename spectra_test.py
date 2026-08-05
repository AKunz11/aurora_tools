#%% Stuff
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import math
from datetime import datetime
from collections import defaultdict
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.ndimage import uniform_filter1d
from matplotlib.patches import Circle

plt.style.use('dark_background')

mag_cmap = plt.get_cmap('Greys') # use for open field line probability, stays consistent with Johnston et al. 2023 
mag_cmap.set_bad((1, 1, 1)) # this does... something lol 
map_img = np.load(r'D:/bfield_smoothed.npy', allow_pickle=False)


#%% Get files
direc='D:/nightglow/spectra_out'
orbit_number='09300'
scan_num=12
file_list=glob.glob(direc)
#print(file_list)

files=os.listdir(direc)
#print(files)

data = np.load(f"D:/nightglow/spectra_out/orbit{orbit_number}_spectra.npz", allow_pickle=True)
items=data['items']
spec_data=items[scan_num-1] #Has keys like orbit, scan, wavelength_nm, background_kR, aurora_fit_kR, r_squared, pearson_r, co_average_kR, co2p_average_kR, sza_deg, n_pixels, flag, anomalous
#print(spec_data)



#%% Big Function
# --- paths (match your stats.py) ---
ql_path    = "D:/nightglow/tables/"
class_path = "D:/nightglow/class_tables/"

def open_ql_table(start_str, stop_str):
    return pd.read_csv(f"{ql_path}{start_str}_{stop_str}_detections_short_1.csv", header=0)

def open_class_table(start_int, stop_int, clearNONE=True):
    # class table filenames: aurora_{start}_{stop} - Sheet1.csv
    df = pd.read_csv(f"{class_path}aurora_{start_int}_{stop_int} - Sheet1.csv", header=0)
    if clearNONE:
        df = df[df["type"] != "NONE"]
    return df

def merged_orbit_block_df(orbit_int):
    """
    For an orbit (e.g., 9300), open the 9200_9300 or 9300_9400 block files,
    merge QL table with class table, and return merged DF.
    """
    orbit1 = (orbit_int // 100) * 100  # floor to nearest 100

    # build zero-padded strings for QL filename
    if orbit1 < 10000:
        start_str = f"0{orbit1:04d}"
        stop_str  = f"0{orbit1+100:04d}"
    else:
        start_str = str(orbit1)
        stop_str  = str(orbit1+100)

    ql_df    = open_ql_table(start_str, stop_str)
    class_df = open_class_table(orbit1, orbit1+100)

    # merge: keep all QL rows, bring in class "type" by orbit_number
    # (matching your stats.py approach)
    merged = pd.merge(
        ql_df,
        class_df.drop("pearson_r", axis=1, errors="ignore"),
        on="orbit_number",
        how="left",
    )
    return merged


def gather_spectra(orb_start,orb_stop,plot=False):
    orb_list=[]
    for orbit in range(orb_start,orb_stop+1):
        if orbit<10000:
            orbit_str = f"0{orbit:04d}"
        else:
            orbit_str = str(orbit)
            
        try:
            file_path=f'D:/nightglow/spectra_out/orbit{orbit_str}_spectra.npz'
            data = np.load(file_path, allow_pickle=True)
            
            orbit1=(orbit//100)*100 #Rounds down to nearest 100
            if orbit1<10000:
                orbit1_str_start = f"0{orbit1:04d}"
                orbit1_str_end = f"0{orbit1+100:04d}"
            else:
                orbit1_str_start = str(orbit1)
                orbit1_str_end = str(orbit1+100)
            
            df = merged_orbit_block_df(orbit)
            
            items=data['items']
            scan_list=[]
            
            if plot:
                fig, axs=plt.subplots(math.ceil(len(items)/2),2,figsize=(12,18),tight_layout=True)
                axes=axs.flatten()
            for i, spec_data in enumerate(items):
                scan = spec_data['scan']
                wavelength=spec_data['wavelength_nm']
                background=spec_data['background_kR']
                fit=spec_data['aurora_fit_kR']
                print(f'\rGot spectra data for orbit {orbit} scan {scan}')
                
                if np.all(np.isnan(background)):
                    #print(f'No spectra data for scan {scan}')
                    if plot:
                        axes[scan-1].yaxis.set_visible(False)
                        axes[scan-1].xaxis.set_visible(False)
                    continue
                
                #Data
                wavelength=spec_data['wavelength_nm']
                background=spec_data['background_kR']
                fit=spec_data['aurora_fit_kR']
                rcoeff=np.abs(spec_data["pearson_r"])
                sza=spec_data['sza_deg']
                n_pixels=spec_data['n_pixels']  
                
                #Radiances
                coavg=spec_data['co_average_kR']
                co2avg=spec_data['co2p_average_kR']
                ratio=coavg/co2avg
                spec_data['ratio']=ratio
                
                #Geoms
                mask = (df["orbit_number"] == orbit) & (df["scan"] == scan)
                type_series = df.loc[mask, "type"] if "type" in df.columns else pd.Series([], dtype=object)
                spec_type = str(type_series.iloc[0]) if len(type_series) > 0 else "UNKNOWN"
                spec_data["type"] = spec_type
                
                if spec_type == "NON-DET":
                    # skip this scan entirely
                    continue
                lat_series = df[mask]['latitude']
                spec_data['latitude'] = float(lat_series.iloc[0]) if len(lat_series) > 0 else np.nan
                lon_series = df[mask]['longitude']
                spec_data['longitude'] = float(lon_series.iloc[0]) if len(lon_series) > 0 else np.nan
                ls=df[mask]['solar_longitude']
                
                date_series = df.loc[mask, "date"]
                if len(date_series) > 0:
                    date_str = str(date_series.iloc[0])
                    spec_data["date"] = pd.to_datetime(date_str, format="%Y-%b-%d", errors="coerce")
                else:
                    spec_data["date"] = pd.NaT
                
                
                loc_time=df[mask]['local_time']
                if len(loc_time) > 0:
                    spec_data['local_time'] = float(loc_time.iloc[0])
                else:
                    spec_data['local_time'] = np.nan
                    
                if len(ls) > 0:
                    spec_data['l_s'] = float(ls.iloc[0])
                else:
                    spec_data['l_s'] = np.nan
                    
                lt = spec_data['local_time']
                if not np.isnan(lt):
                    spec_data['hours_from_midnight'] = lt if lt <= 12 else lt - 24
                else:
                    spec_data['hours_from_midnight'] = np.nan
                
                #Flags
                sza_min=100 #Arbitrary
                r_min=.55 #Schneider uses .55
                n=3 #Schneider uses 3
                min_ratio=12.7
                if (sza>=sza_min) & (n_pixels>=n) & (rcoeff>=r_min):
                    spec_data['flag']=1
                else:
                    spec_data['flag']=0
                
                if ratio>=min_ratio:
                    spec_data['anomalous']=1
                else:
                    spec_data['anomalous']=0
                
                flag=spec_data['flag']
                anomalous=spec_data['anomalous']
                 
                if plot:
                     
                    #Fit region lines
                    minwave_ind = np.argmin(np.abs(wavelength - 190))
                    maxwave_ind = np.argmin(np.abs(wavelength - 246))
                    axes[scan-1].axvline(wavelength[minwave_ind], color='grey', linestyle=':', linewidth=0.5)
                    axes[scan-1].axvline(wavelength[maxwave_ind], color='grey', linestyle=':', linewidth=0.5)
                    
                    #Actual spectra and template
                    axes[scan-1].plot(wavelength,background,c='grey',label='Observed')
                    axes[scan-1].plot(wavelength,fit,c='r',ls='--',label='Fit')
                    axes[scan-1].yaxis.set_visible(False)
                    axes[scan-1].xaxis.set_visible(False)
                    
                    #Labels
                    if flag==1:
                        flag_color='g'
                    else:
                        flag_color='r'
                    axes[scan-1].text(0.98, 0.95, f'\nScan {spec_data["scan"]}', c=flag_color, ha='right', va='top', transform=axes[scan-1].transAxes)
                    axes[scan-1].text(0.98, 0.95, f'\n\nN = {n_pixels} CO = {coavg:.2f} CO2p = {co2avg:.2f} R = {rcoeff:.2f}', ha='right', va='top', transform=axes[scan-1].transAxes)
                    axes[scan-1].text(0.98, 0.95, f'\n\n\nRatio = {ratio:.2f}', ha='right', va='top', transform=axes[scan-1].transAxes)
                    
                scan_list.append(spec_data)
            
            #fig.subplots_adjust(wspace=0, hspace=0)
            if scan_list:
                orb_list.append(scan_list)
            if plot:
                plt.suptitle(f'Spectra for Orbit {orbit_str}', fontsize=26, fontweight='bold')
                plt.savefig(f'D:/nightglow/spectra_out/plots/orbit{orbit_str}.png')
                
        except FileNotFoundError:
            print(f'No data for orbit {orbit}')
            
    return orb_list

#%% Isolate spectra

def isolate_spectrum(orbit, scan, orb_list):
    for orbit_scans in orb_list:              # orbit_scans is a list of scan dicts for one orbit
        if not orbit_scans:
            continue

        # each dict has the same orbit number within this orbit_scans list
        if orbit_scans[0].get('orbit') != orbit:
            continue

        for s in orbit_scans:
            if s.get('scan') == scan:
                return s

    return None

        
def isolate_anomalous(orb_list,text=False):
    anom_dict=defaultdict(list)
    norm_dict=defaultdict(list)
    for o in orb_list:
        orbit_num = o[0]['orbit']
        for s in o:
            if s['flag']==1:
                if s['anomalous']==1:
                    anom_dict[orbit_num].append(s)
                else:
                    norm_dict[orbit_num].append(s)
                    
    anom=dict(anom_dict)
    norm=dict(norm_dict)
    
    if text:
        print('\nAnomalous'+'-'*100)
        for i in anom.keys():
            for s in anom[i]:
                print(f'Orbit {s["orbit"]} | Scan {s["scan"]} | R {s["pearson_r"]:.2f} | CO {s["co_average_kR"]:.2f}\n')
        
        print('Normal'+'-'*100)
        for i in norm.keys():
            for s in norm[i]:
                print(f'Orbit {s["orbit"]} | Scan {s["scan"]} | R {s["pearson_r"]:.2f} | CO {s["co_average_kR"]:.2f}\n')
    return anom, norm
    
#%% Plot Comparison

def plot_compare(norm,anom,scale=.8):
    # Get data
    wavelength_norm=norm['wavelength_nm']
    background_norm=norm['background_kR']
    smooth_norm=uniform_filter1d(background_norm,10)
    fit_norm=norm['aurora_fit_kR']
    
    wavelength_anom=anom['wavelength_nm']
    background_anom=anom['background_kR']
    smooth_anom=uniform_filter1d(background_anom,10)
    fit_anom=anom['aurora_fit_kR']
    
    scale1=np.max(smooth_norm)/np.max(smooth_anom)
    
    # Plot
    fig, axs=plt.subplots(1,3,figsize=(12,4),tight_layout=True)
    axes=axs.flatten()
    
    axes[0].plot(wavelength_norm,background_norm,c='grey',alpha=.5,label='Observed')
    axes[0].plot(wavelength_norm,fit_norm,c='r',alpha=.5,ls='--',label='Fit')
    axes[0].yaxis.set_visible(False)
    axes[0].xaxis.set_visible(True)
    axes[0].set_title(f'Normal Spectrum\n Orbit {norm["orbit"]} scan {norm["scan"]}')
    axes[0].legend()
    
    axes[1].plot(wavelength_anom,background_anom,c='lightgrey',alpha=.5,label='Observed')
    axes[1].plot(wavelength_anom,fit_anom,c='b',alpha=.5,ls='--',label='Fit')
    axes[1].yaxis.set_visible(False)
    axes[1].xaxis.set_visible(True)
    axes[1].set_title(f'Anomalous Spectrum\n Orbit {anom["orbit"]} scan {anom["scan"]}')
    axes[1].legend()
    
    axes[2].plot(wavelength_norm[0:256],background_norm[0:256],c='grey',alpha=.5,label='Observed (Normal)')
    axes[2].plot(wavelength_norm[0:256],fit_norm[0:256],c='r',alpha=.5,label='Fit (Normal)')
    axes[2].plot(wavelength_anom[0:256],background_anom[0:256],c='lightgrey',alpha=.5,label='Observed (Anomalous)')
    axes[2].plot(wavelength_anom[0:256],fit_anom[0:256],c='b',alpha=.5,label='Fit (Anomalous)')
    axes[2].yaxis.set_visible(False)
    axes[2].xaxis.set_visible(True)
    axes[2].set_title('Over-plotted Cameron System')
    
    # Smooth Plot
    fig, axs=plt.subplots(1,3,figsize=(12,4),tight_layout=True)
    axes=axs.flatten()
    
    axes[0].plot(wavelength_norm,smooth_norm,c='grey',alpha=.5,label='Observed')
    #axes[0].plot(wavelength_norm,fit_norm,c='r',alpha=.5,ls='--',label='Fit')
    axes[0].yaxis.set_visible(False)
    axes[0].xaxis.set_visible(True)
    axes[0].set_title(f'Smoothed Normal Spectrum\n Orbit {norm["orbit"]} scan {norm["scan"]}')
    axes[0].legend()
    
    axes[1].plot(wavelength_anom,smooth_anom,c='lightgrey',alpha=.5,label='Observed')
    #axes[1].plot(wavelength_anom,fit_anom,c='b',alpha=.5,ls='--',label='Fit')
    axes[1].yaxis.set_visible(False)
    axes[1].xaxis.set_visible(True)
    axes[1].set_title(f'Smoothed Anomalous Spectrum\n Orbit {anom["orbit"]} scan {anom["scan"]}')
    axes[1].legend()
    
    axes[2].plot(wavelength_norm[0:256],smooth_norm[0:256],c='grey',alpha=.5,label='Observed (Normal)')
    #axes[2].plot(wavelength_norm[0:256],fit_norm[0:256],c='r',alpha=.5,label='Fit (Normal)')
    axes[2].plot(wavelength_anom[0:256],smooth_anom[0:256]*scale1,c='lightgrey',alpha=.5,label='Observed (Anomalous)')
    #axes[2].plot(wavelength_anom[0:256],fit_anom[0:256],c='b',alpha=.5,label='Fit (Anomalous)')
    axes[2].yaxis.set_visible(False)
    axes[2].xaxis.set_visible(True)
    axes[2].set_title('Over-plotted Cameron System')
    
    plt.figure()
    plt.plot(wavelength_norm[0:256],smooth_norm[0:256],c='grey',alpha=.5)
    plt.plot(wavelength_norm[0:256],fit_norm[0:256],c='r',alpha=.5,label=f'Fit (Normal)\nCO: {norm["co_average_kR"]:.2f}')
    plt.plot(wavelength_anom[0:256],smooth_anom[0:256]*scale1,c='lightgrey',alpha=.5)
    plt.plot(wavelength_anom[0:256],fit_anom[0:256]*scale1,c='b',alpha=.5,label=f'Fit (Anomalous)\nCO: {anom["co_average_kR"]:.2f} ')
    plt.title(f'Over-plotted Cameron System (Scale = {scale1:.3f})')
    plt.legend(fontsize='small')
    
    plt.figure()
    fig,axs=plt.subplots()
    mag_topo = plt.imshow(map_img, cmap=mag_cmap, norm=colors.LogNorm(vmin=0.001, vmax=1), origin='lower', extent=[0, 360, -90, 90])
    divider = make_axes_locatable(axs)
    axs.scatter(norm['longitude'],norm['latitude'],s=8,c='r',label='Normal')
    axs.scatter(anom['longitude'],anom['latitude'],s=8,c='b',label='Anomalous')
    cax = divider.append_axes("right", size="5%", pad=0.2, aspect=10)
    cbar_map = fig.colorbar(mag_topo, cax=cax)
    tick_locations = [.001, .01, .1, 1]
    cbar_map.set_ticks(tick_locations)
    cbar_map.set_ticklabels([str(tick) for tick in tick_locations])
    cbar_map.set_label('Magnetic Topology')
    cbar_map.ax.yaxis.set_label_position('left')
    axs.set_xlabel('Longitude')
    axs.set_ylabel('Latitude')
    axs.set_title('Location of Detections')
    axs.legend()
    
    return
    


def bright_compare(norm,anom,num_plots):
    norm=norm[::-1]
    anom=anom[::-1]
    
    #Norm Plots
    fig, axs=plt.subplots(int(num_plots/2),2,figsize=(10,20),tight_layout=True)
    axes=axs.flatten()
    for i in range(num_plots):
        if len(norm[i]['wavelength_nm'])==512:
            axes[i].plot(norm[i]['wavelength_nm'],norm[i]['background_kR'],label=f'Orbit/Scan: {norm[i]["orbit"]}/{norm[i]["scan"]}\nr: {norm[i]["pearson_r"]:.2f}')
            axes[i].yaxis.set_visible(False)
            axes[i].xaxis.set_visible(False)
            axes[i].legend()
            if i==int(num_plots-2) or i==int(num_plots-1):
                axes[i].xaxis.set_visible(True)
                axes[i].set_xlabel('Wavelength (nm)')
    plt.suptitle(f'{num_plots} Brightest Normal Detections')
    plt.savefig(f'D:/nightglow/spectra_out/plots/bright{num_plots}_norm.pdf')
    
    #Anom Plots
    fig, axs=plt.subplots(int(num_plots/2),2,figsize=(10,20),tight_layout=True)
    axes=axs.flatten()
    for i in range(num_plots):
        if len(anom[i]['wavelength_nm'])==512:
            axes[i].plot(anom[i]['wavelength_nm'],uniform_filter1d(anom[i]['background_kR'],5),label=f'Orbit/Scan: {anom[i]["orbit"]}/{anom[i]["scan"]}\nr: {anom[i]["pearson_r"]:.2f}')
            axes[i].yaxis.set_visible(False)
            axes[i].xaxis.set_visible(False)
            axes[i].legend()
            if i==int(num_plots-2) or i==int(num_plots-1):
                axes[i].xaxis.set_visible(True)
                axes[i].set_xlabel('Wavelength (nm)')
    plt.suptitle(f'{num_plots} Brightest Anomalous Detections')
    plt.savefig(f'D:/nightglow/spectra_out/plots/bright{num_plots}_anom.pdf')
    
def seasonal_plots(norm, anom, polar=False, ratio=True, cmap_name="twilight_shifted"):
    """
    Plots Normal vs Anomalous detections colored by L_s.

    Fixes:
      - single scatter per axis (colorbar matches points)
      - shared cmap + shared Normalize between panels
      - correct degree->radian conversion for latitude in polar projection
    """

    # ---------- helper to flatten dict-of-lists into a list of dicts ----------
    
    # ---------- ratio plots ----------
    if ratio:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        axes = axs.flatten()

        if norm_ls.size > 0 and norm_rat.size > 0:
            axes[0].scatter(norm_ls, norm_rat, s=8)
        axes[0].set_xlabel("Solar Longitude (L_s)")
        axes[0].set_ylabel("CO / CO2+ (ratio)")
        axes[0].set_title("Normal")

        if anom_ls.size > 0 and anom_rat.size > 0:
            axes[1].scatter(anom_ls, anom_rat, s=8)
        axes[1].set_xlabel("Solar Longitude (L_s)")
        axes[1].set_ylabel("CO / CO2+ (ratio)")
        axes[1].set_title("Anomalous")

    return

def ls_gaps(norm, anom):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4), tight_layout=True)
    axes = axs.flatten()

    n0 = 0
    n1 = 0

    for o, scans in norm.items():
        for s in scans:
            dt = s.get("date", pd.NaT)
            ls = s.get("l_s", np.nan)
            if pd.isna(dt) or not np.isfinite(ls):
                continue
            axes[0].scatter(dt, ls, s=6)
            n0 += 1

    for o, scans in anom.items():
        for s in scans:
            dt = s.get("date", pd.NaT)
            ls = s.get("l_s", np.nan)
            if pd.isna(dt) or not np.isfinite(ls):
                continue
            axes[1].scatter(dt, ls, s=6)
            n1 += 1

    axes[0].set_title(f"Normal (n={n0})")
    axes[1].set_title(f"Anomalous (n={n1})")
    for ax in axes:
        ax.set_xlabel("Date")
        ax.set_ylabel("L_s")
        ax.tick_params(axis="x", rotation=30)

    plt.show()

#%% Running
orb_list=gather_spectra(2000,12000,plot=False)
anom,norm=isolate_anomalous(orb_list)

all_norm_sorted = sorted(
    (s for scans in norm.values() for s in scans),
    key=lambda x: x['co_average_kR'])

all_anom_sorted = sorted(
    (s for scans in anom.values() for s in scans),
    key=lambda x: x['co_average_kR'])

#Anom: 24367 Scan 10
#Norm: 24446 Scan 10

#plot_compare(norm[24446][-1], anom[24367][-2],scale=1.711)
#Setting scale = CO_norm / CO_anom gives really good match

#coadded(norm, anom, localtime=True)
#bright_compare(all_norm_sorted, all_anom_sorted, int(20))
seasonal_plots(norm, anom, polar=True, ratio=True)
ls_gaps(norm,anom)

#goal=isolate_spectrum(12555, 12, orb_list)
#print(goal)
#print(len(goal['background_kR']))




