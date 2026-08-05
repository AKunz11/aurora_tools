import matplotlib.pyplot as plt
import numpy as np

def latitude_hist(data,key):
    fig,axs=plt.subplots()
    
    lat_edges_deg=np.arange(-90, 90, 20)
    le_rad=np.deg2rad(lat_edges_deg)
    geom_lat_w=(np.sin(le_rad[1:]) - np.sin(le_rad[:-1]))
    geom_lat_w/=geom_lat_w.sum()
    lat_counts,_=np.histogram(data['latitude'], bins=lat_edges_deg)
    N=lat_counts.sum()
    expected_lat=geom_lat_w*N
    widths = np.diff(lat_edges_deg)
    
    bin_centers=0.5*(lat_edges_deg[:-1]+lat_edges_deg[1:])
    axs.bar(bin_centers, lat_counts, width=widths, edgecolor='black', align='center', alpha=0.6, label='Detections')
    axs.plot(bin_centers, expected_lat, '--', lw=2, c='black', label='Uniform (geometry)')
    axs.errorbar(bin_centers, lat_counts, yerr=np.sqrt(lat_counts), fmt='none')
    axs.set_xlabel('Latitude ($^\circ$)'); axs.set_ylabel('Counts'); axs.set_title(f'Latitude ({key})'); axs.legend()
    axs.set_xticks(np.arange(-90,91,20))
    axs.set_xlim(-90,90)
    plt.savefig(f'D:/thesis_images/lat_{key}.png', dpi=300)
    plt.show()
    return