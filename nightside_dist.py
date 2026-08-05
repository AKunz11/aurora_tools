import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib import colors

def nightside_dist(data,key,start,stop,label=False):
    lat = np.asarray(data['latitude'], dtype=float)
    ls  = np.asarray(data['solar_longitude'], dtype=float)
    lt = np.asarray(data['local_time'], dtype=float)  # must exist
    mso_lon= np.asarray(data['mso_longitude'], dtype=float)
    mso_lat= np.asarray(data['mso_latitude'], dtype=float)

    if 'hours_from_midnight' in data.columns:
        hfm = np.asarray(data['hours_from_midnight'], dtype=float)
    else:
        lt = np.asarray(data['local_time'], dtype=float)  # must exist
        hfm = np.where(lt <= 12, lt, lt - 24)

    ok = np.isfinite(lat) & np.isfinite(hfm)
    orbit = np.asarray(data['orbit_number'])[ok]
    lat = lat[ok]
    hfm = hfm[ok]
    ls = ls[ok]
    lt = lt[ok]
    mso_lon = mso_lon[ok]
    mso_lat = mso_lat[ok]

    #Polar
    theta = (2 * np.pi / 24.0) * hfm
    lat_rad = np.deg2rad(lat)
    mso_lon_rad = np.deg2rad(mso_lon)
    mso_lat_rad = np.deg2rad(mso_lat)
    phi = np.deg2rad(mso_lon - 180.0)     # put midnight at center

    x = np.cos(mso_lat_rad) * np.sin(mso_lon_rad)
    y = -np.sin(mso_lat_rad)

    #Polar scatter plot
    fig, ax = plt.subplots(figsize=(6, 6))
    sc = ax.scatter(x, y, s=5, c=ls, cmap='twilight_shifted', norm=colors.Normalize(vmin=0, vmax=360), alpha=0.9)
    # Orbit labels
    if label:
        for xi, yi, orb in zip(x, y, orbit): #put off center and rotate 45 degrees for better visibility
            ax.text(
                xi+0.04, yi+0.04,
                str(orb),
                fontsize=4,
                ha='center',
                va='center',
                alpha=0.7,
                rotation=45

            )
    
    #SZA rings
    szas = [160, 140, 120, 110, 100, 90]
    for sza in szas:
        psi = np.deg2rad(180 - sza)
        r = np.sin(psi)

        circ0 = Circle((0, 0), r, fill=False, linestyle="--", linewidth=.5, alpha=0.6)
        ax.add_patch(circ0)
        ax.text(0, r, f"{sza}°", va="bottom", ha="left", fontsize=8, alpha=0.8)


    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("L$_s$")
    plt.title(f'Nightside Distribution - {key}', fontsize=16)
    plt.savefig(f'D:/thesis_images/night_{key}.png', dpi=600)
    plt.show()


    heat=False
    if heat:
        # Polar heatmap
        nbins = 30
        H, xedges, yedges = np.histogram2d(x, y, bins=nbins, range=[[-1, 1], [-1, 1]])

        fig, ax = plt.subplots(figsize=(6, 6))

        cmap = plt.get_cmap("inferno").copy()
        cmap.set_under("black")  # color for values below vmin

        im = ax.imshow(
            H.T,
            origin="lower",
            extent=[-1, 1, -1, 1],
            cmap=cmap,
            vmin=1e-9  #lower limit (allows bins to be filled with 0)
        )

        szas = [160, 140, 120, 100, 90]
        for sza in szas:
            psi = np.deg2rad(180 - sza)
            r = np.sin(psi)

            circ0 = Circle((0, 0), r, fill=False, linestyle="--", linewidth=1, alpha=0.6, color='white')
            ax.add_patch(circ0)
            #Make text show at 45 degrees for better visibility
            ax.text(r * np.cos(np.pi/4), r * np.sin(np.pi/4), f"{sza}°", va="bottom", ha="left", fontsize=8, alpha=0.8, color='white')
        
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        plt.colorbar(im, ax=ax, label="Counts per bin")
        plt.title(f'Nightside Distribution Heatmap - {key}')
        plt.savefig(f'D:/thesis_images/heatmap_{key}.png', dpi=300)
        plt.show()


    cart=False
    if cart:
        #Cartesian
        fig, ax = plt.subplots(figsize=(7, 4))
        sc = ax.scatter(hfm, lat, c=ls, s=8, cmap='twilight_shifted', norm=colors.Normalize(vmin=0, vmax=360), alpha=0.9)

        #Add orbit labels
        if label:
            for h, la, orb in zip(hfm, lat, orbit):
                ax.text(
                    h, la,
                    str(orb),
                    fontsize=6,
                    ha='center',
                    va='center',
                    alpha=0.7
                )

        ax.set_xlabel("Hours from midnight")
        ax.set_ylabel("Latitude ($^\circ$)")

        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("L$_s$")

        plt.title(f'Nightside Distribution - {key}', fontsize=16)
        plt.savefig(f'D:/thesis_images/nightscatter_{key}.png', dpi=300)
        plt.show()
    
    return