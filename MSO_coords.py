"""Convert Mars planetocentric coordinates to Mars-Sun Orbital coordinates.

The module loads the configured NAIF SPICE kernels when imported. Update the
kernel paths below before using these conversion functions on another system.
"""

import numpy as np
import spiceypy as spice
from pathlib import Path

SPICE_ROOT = Path(__file__).resolve().parent / 'spice'
SPICE_KERNELS = (
    SPICE_ROOT / 'LSK' / 'naif0012.tls',
    SPICE_ROOT / 'PCK' / 'pck00010.tpc',
    SPICE_ROOT / 'SPK' / 'mar097.bsp',
)
_kernels_loaded = False


def load_spice_kernels():
    """Load the project-local SPICE kernels once."""
    global _kernels_loaded
    if _kernels_loaded:
        return

    missing = [str(path) for path in SPICE_KERNELS if not path.is_file()]
    if missing:
        missing_list = '\n  - '.join(missing)
        raise FileNotFoundError(
            f"Missing required SPICE kernels:\n  - {missing_list}\n"
            "Place them under the project's spice/ directory as described "
            "in README.md."
        )

    for kernel_path in SPICE_KERNELS:
        spice.furnsh(str(kernel_path))
    _kernels_loaded = True

def planetocentric_to_planetographic(lat_c_deg):
    """Convert a Mars planetocentric latitude in degrees to planetographic."""
    radii = spice.bodvrd("MARS", "RADII", 3)[1]
    re, _, rp = radii
    lat_c = np.deg2rad(lat_c_deg)
    lat_g = np.arctan((re**2 / rp**2) * np.tan(lat_c))
    return np.rad2deg(lat_g)

def mars_geodetic_to_cart(lat_centric_deg,lon,alt=0):
    """Return an IAU_MARS Cartesian position for a latitude and longitude.

    Args:
        lat_centric_deg: Planetocentric latitude in degrees.
        lon: East longitude in degrees.
        alt: Altitude above the reference ellipsoid in kilometers.
    """
    #Check: Assume alt is from ellipsoid
    radii=spice.bodvrd('MARS', 'RADII', 3)[1]
    re,_,rp=radii

    f=(re-rp)/re

    lat_graphic_deg = planetocentric_to_planetographic(lat_centric_deg)

    lon=np.deg2rad(lon)
    lat=np.deg2rad(lat_graphic_deg)

    x,y,z=spice.georec(lon,lat,alt,re,f)
    return np.array([x,y,z])

def build_mso_rotation(et):
    """Build the J2000-to-MSO rotation matrix at ephemeris time ``et``."""
    state,_=spice.spkezr('MARS',et,'J2000','NONE','SUN')
    r_mars=state[:3]
    v_mars=state[3:]

    #MSO axes
    x_hat=spice.vhat(-r_mars) #+X points towards the Sun
    z_hat=spice.vhat(spice.vcrss(x_hat,v_mars))
    y_hat = spice.vhat(spice.vcrss(z_hat, x_hat))

    # re-orthogonalize z for numerical cleanliness
    z_hat = spice.vhat(spice.vcrss(x_hat, y_hat))

    rot=np.vstack([x_hat,y_hat,z_hat])
    return rot

def iau_to_mso(r_iau,et):
    """Rotate an IAU_MARS Cartesian position into the MSO frame."""
    rot_body_to_j2000=spice.pxform('IAU_MARS', 'J2000', et)
    r_j2000=rot_body_to_j2000 @ r_iau

    rot_j2000_to_mso=build_mso_rotation(et)
    r_mso=rot_j2000_to_mso @ r_j2000

    return r_mso

def mars_latlon_to_mso(lat,lon,alt,et):
    """Convert a Mars latitude, longitude, altitude, and time to MSO Cartesian."""
    r_iau=mars_geodetic_to_cart(lat,lon,alt)
    r_mso=iau_to_mso(r_iau,et)
    return r_mso

def mso_rect_to_lonlat(r_mso):
    """Convert an MSO Cartesian vector to longitude and latitude in degrees."""
    r,lon,lat=spice.reclat(r_mso)
    lon=np.rad2deg(lon)
    lat=np.rad2deg(lat)
    return lon,lat

#Usage
#lat,lon,alt=10,135,130
#utc='2024-01-01T00:00:00'
#r_mso=mars_latlon_to_mso(lat,lon,alt,utc)
#mso_lon,mso_lat=mso_rect_to_lonlat(r_mso)
#print('MSO Lon:', mso_lon, 'MSO Lat:', mso_lat)

#main function
def mso_coords(data):
    """Add ``mso_longitude`` and ``mso_latitude`` columns to a DataFrame.

    The input must contain ``latitude``, ``longitude``, ``altitude``, and
    SPICE ephemeris time ``et`` columns. The same DataFrame is returned after
    being updated in place.
    """
    load_spice_kernels()

    mso_lons=[]
    mso_lats=[]
    for index, row in data.iterrows():
        lat=row['latitude']
        lon=row['longitude']
        alt=row['altitude']
        et=float(row['et'])
        r_mso=mars_latlon_to_mso(lat,lon,alt,et)
        mso_lon,mso_lat=mso_rect_to_lonlat(r_mso)
        mso_lons.append(mso_lon)
        mso_lats.append(mso_lat)

    data['mso_longitude']=mso_lons
    data['mso_latitude']=mso_lats
    return data




