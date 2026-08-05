import numpy as np
import matplotlib.pyplot as plt

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

# ============================================================
# VALUES USED
# ============================================================
ALT_MIN_KM = 100
ALT_MAX_KM = 250
ALT_STEP_KM = 1

H_CO=17*1e5 # scale height for CO cm
H_CO2=11*1e5 # scale height for CO2 cm
R_MARS_KM=3390*1e5 # Mars radius in cm
ALT_MAX=145
ALT_MAX_CM=ALT_MAX*1e5
R=ALT_MAX_CM+R_MARS_KM

L_CO=np.sqrt(2*np.pi*R*H_CO)
L_CO2=np.sqrt(2*np.pi*R*H_CO2)

REPORT_ALTITUDE_KM = 150
ENERGIES_EV = [16, 18, 20, 30, 40, 50]

# scale the 80 eV flux profile so its top value matches this
JC_FLUX_TARGET = 1.25e10

# ============================================================
# CROSS SECTIONS (cm^2)
# ============================================================
CO2_UVD_XS = {
    16: 0.00e0,
    18: 5.00e-18,
    20: 1.00e-17,
    30: 2.17e-17,
    40: 3.07e-17,
    50: 3.77e-17,
    100: 5.58e-17,
}

CO2_UVD_XS2 = {
    16: 0.00e0,
    18: 0.0121e-16,
    20: 0.0247e-16,
    30: 0.120e-16,
    40: 0.191e-16,
    50: 0.256e-16,
    100: 0.434e-16,
}

CO2_CAM_XS = {
    16: 3.53e-17,
    18: 4.38e-17,
    20: 4.24e-17,
    30: 9.34e-18,
    40: 5.51e-18,
    50: 4.80e-18,
    100: 3.60e-18,
}

CO_CAM_XS = {
    16: 4.14e-17,
    18: 2.23e-17,
    20: 1.32e-17,
    30: 4.80e-18,
    40: 6.00e-18,
    50: 6.54e-18,
    100: 7.77e-18,
}

# ============================================================
# FILES
# ============================================================
CO2_DENSITY_FILE = "data/jc_co2_density.csv"
CO_DENSITY_FILE = "data/jc_co_density.csv"
CO2P_DENSITY_FILE = "data/jc_co2p_density.csv"
EFLUX_FILE = "data/eflux_alt_80.csv"
ETEMP_FILE = "data/e_temps.csv"
E_DENSITY_FILE = "data/e_ion_density_alt.csv"

# ============================================================
# UNITS
# ============================================================
# altitude:       km
# density:        cm^-3
# e_flux:         cm^-2 s^-1 eV^-1
# cross section:  cm^2
# VER:            cm^-3 s^-1 eV^-1
# ============================================================


def load_profile(filename, delimiter=",", skiprows=1, usecols=(0, 1)):
    """
    Returns:
        values, altitude
    Assumes file columns are [value, altitude]
    """
    arr = np.loadtxt(filename, delimiter=delimiter, skiprows=skiprows, usecols=usecols)
    values = arr[:, 0]
    altitude = arr[:, 1]
    return values, altitude


def interp_to_grid(alt_src, val_src, alt_grid, log_interp=False):
    """
    Interpolate a profile onto the model altitude grid.
    """
    order = np.argsort(alt_src)
    alt_src = alt_src[order]
    val_src = val_src[order]

    if log_interp:
        mask = val_src > 0
        alt_use = alt_src[mask]
        val_use = val_src[mask]

        if len(val_use) < 2:
            return np.full_like(alt_grid, np.nan, dtype=float)

        log_val = np.log(val_use)
        log_val_i = np.interp(alt_grid, alt_use, log_val, left=np.nan, right=np.nan)
        return np.exp(log_val_i)

    return np.interp(alt_grid, alt_src, val_src, left=np.nan, right=np.nan)


def build_scaled_flux_profile():
    """
    Load the 80 eV flux profile and scale it to the chosen top value.
    """
    flux_val, flux_alt = load_profile(EFLUX_FILE, delimiter=",", skiprows=1, usecols=(0, 1))

    scale = JC_FLUX_TARGET / flux_val[-1]
    flux_val_scaled = flux_val * scale

    return flux_val_scaled, flux_alt


def calculate_ver(density_profile, flux_profile, cross_section):
    """
    VER(z) = n(z) * flux(z) * sigma
    """
    return 4*np.pi* density_profile * flux_profile * cross_section

def calculate_ver_dr(electron_density_profile, ion_density_profile, e_temps):
    k=4.2*10**-7 * (300 / e_temps)**0.75 *.29
    return 4*np.pi* k * electron_density_profile * ion_density_profile


def print_value_at_altitude(label, altitude_grid, density, flux, cross_section, ver, report_alt):
    idx = np.where(altitude_grid == report_alt)[0]
    if len(idx) == 0:
        print(f"{report_alt} km is not in the grid.")
        return

    i = idx[0]

    if "Dissociative Recombination" not in label:
        print("="*20)
        print(f"\n{label}")
        print(f"  altitude       = {altitude_grid[i]:.0f} km")
        print(f"  density        = {density[i]:.3e} cm^-3")
        print(f"  e_flux         = {flux[i]:.3e} cm^-2 s^-1 eV^-1")
        print(f"  cross_section  = {cross_section:.3e} cm^2")
        print(f"  VER            = {ver[i]:.3e} cm^-3 s^-1 eV^-1")

    else:
        print("="*20)
        print(f"\n{label}")
        print(f"  altitude       = {altitude_grid[i]:.0f} km")
        print(f"  electron_density = {density[i]:.3e} cm^-3")
        print(f"  ion_density      = {flux[i]:.3e} cm^-3")
        print(f"  e_temp           = {cross_section[i]:.1f} K")
        print(f"  VER              = {ver[i]:.3e} cm^-3 s^-1 eV^-1")


# ============================================================
# MAIN
# ============================================================
alt_grid = np.arange(ALT_MIN_KM, ALT_MAX_KM, ALT_STEP_KM)

# load densities
co2_val, co2_alt = load_profile(CO2_DENSITY_FILE, delimiter=",", skiprows=1, usecols=(0, 1))
co_val, co_alt = load_profile(CO_DENSITY_FILE, delimiter=",", skiprows=1, usecols=(0, 1))
co2p_val, co2p_alt = load_profile(CO2P_DENSITY_FILE, delimiter=",", skiprows=1, usecols=(0, 1))
e_temp_val, e_temp_alt = load_profile(ETEMP_FILE, delimiter=",", skiprows=1, usecols=(0, 1))
e_density_val, e_density_alt = load_profile(E_DENSITY_FILE, delimiter=",", skiprows=1, usecols=(0, 1))
# load and scale flux
flux_val, flux_alt = build_scaled_flux_profile()

# interpolate everything to one altitude grid
co2_density = interp_to_grid(co2_alt, co2_val, alt_grid, log_interp=True)
co_density = interp_to_grid(co_alt, co_val, alt_grid, log_interp=True)
e_flux = interp_to_grid(flux_alt, flux_val, alt_grid, log_interp=True)
e_temp = interp_to_grid(e_temp_alt, e_temp_val, alt_grid, log_interp=True)
e_density = interp_to_grid(e_density_alt, e_density_val, alt_grid, log_interp=True)
co2p_density = interp_to_grid(co2p_alt, co2p_val, alt_grid, log_interp=True)

ratios = []
krs = []
kR_ratios=[]
limbs=[]

for energy in ENERGIES_EV:
    plt.figure(figsize=(8, 6))

    # reaction 1: e + CO2 -> UVD
    xs_co2_uvd = CO2_UVD_XS[energy]
    ver_co2_uvd = calculate_ver(co2_density, e_flux, xs_co2_uvd)
    print_value_at_altitude(
        f"Electron impact on CO2 (UVD), {energy} eV",
        alt_grid, co2_density, e_flux, xs_co2_uvd, ver_co2_uvd, REPORT_ALTITUDE_KM
    )
    plt.semilogx(ver_co2_uvd, alt_grid, label='Electron impact on CO2 (UVD)')

    # reaction 2: e + CO2 -> CAM
    xs_co2_cam = CO2_CAM_XS[energy]
    ver_co2_cam = calculate_ver(co2_density, e_flux, xs_co2_cam)
    print_value_at_altitude(
        f"Electron impact on CO2 (CAM), {energy} eV",
        alt_grid, co2_density, e_flux, xs_co2_cam, ver_co2_cam, REPORT_ALTITUDE_KM
    )
    plt.semilogx(ver_co2_cam, alt_grid, label='Electron impact on CO2 (CAM)')

    # reaction 3: e + CO -> CAM
    xs_co_cam = CO_CAM_XS[energy]
    ver_co_cam = calculate_ver(co_density, e_flux, xs_co_cam)
    print_value_at_altitude(
        f"Electron impact on CO (CAM), {energy} eV",
        alt_grid, co_density, e_flux, xs_co_cam, ver_co_cam, REPORT_ALTITUDE_KM
    )
    plt.semilogx(ver_co_cam, alt_grid, label='Electron impact on CO (CAM)')

    # reaction 4: DR
    ver_dr = calculate_ver_dr(e_density, co2p_density, e_temp)
    print_value_at_altitude(
        f"Dissociative Recombination, {energy} eV",
        alt_grid, e_density, co2p_density, e_temp, ver_dr, REPORT_ALTITUDE_KM
    )
    plt.semilogx(ver_dr, alt_grid, label='Dissociative Recombination (CAM)')


    plt.xlabel("VER (cm$^{-3}$ s$^{-1}$)")
    plt.ylabel("Altitude (km)")
    plt.title(f"VER Profiles at {energy} eV")
    plt.ylim(120, 200)
    plt.xlim(1e-3, None)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # peak value index
    idx_145 = np.argmin(np.abs(alt_grid - 145))

    # total VERs
    ver_total_uvd = ver_co2_uvd
    ver_total_cam = ver_co2_cam + ver_co_cam + ver_dr

    # total peak VERs
    ver_peak_uvd = ver_co2_uvd[idx_145]
    ver_peak_cam = ver_co2_cam[idx_145] + ver_co_cam[idx_145] + ver_dr[idx_145]

    # ratio profile
    ratio_cam_uvd = ver_peak_cam / ver_peak_uvd
    ratios.append((energy, ratio_cam_uvd))

    # vertical integration
    dz_cm = ALT_STEP_KM * 1e5
    intensity_e_on_co2_uvd = np.nansum(ver_co2_uvd * dz_cm)
    intensity_e_on_co2_cam = np.nansum(ver_co2_cam * dz_cm)
    intensity_e_on_co_cam = np.nansum(ver_co_cam * dz_cm)
    intensity_dr = np.nansum(ver_dr * dz_cm)
    intensity_uvd = intensity_e_on_co2_uvd
    intensity_cam = intensity_e_on_co2_cam+intensity_e_on_co_cam+intensity_dr

    # convert to kR
    kR_e_on_co2_uvd = intensity_e_on_co2_uvd / (1e9)
    kR_e_on_co2_cam = intensity_e_on_co2_cam / (1e9)
    kR_e_on_co_cam = intensity_e_on_co_cam / (1e9)
    kR_dr = intensity_dr / (1e9)
    kR_uvd = intensity_uvd / (1e9)
    kR_cam = intensity_cam / (1e9)
    kR_ratio=kR_cam/kR_uvd

    kR_ratios.append((energy,kR_ratio))

    krs.append((energy, kR_e_on_co2_uvd, kR_e_on_co2_cam, kR_e_on_co_cam, kR_dr, kR_uvd, kR_cam, ratio_cam_uvd))

    # limb intensity profiles
    idx_max=np.where(alt_grid == ALT_MAX)[0][0] #145 km index
    
    I_limb_e_on_co=L_CO*ver_co_cam[idx_max]/(4*np.pi)/ 1e9
    I_limb_e_on_co2_cam=L_CO2*ver_co2_cam[idx_max]/(4*np.pi)/ 1e9
    I_limb_e_on_co2_uvd=L_CO2*ver_co2_uvd[idx_max]/(4*np.pi)/ 1e9
    I_limb_dr=L_CO2*ver_dr[idx_max]/(4*np.pi)/ 1e9

    #dr_avg=L_CO2*np.nanmean(ver_dr)/ 1e9

    I_limb_cam=I_limb_e_on_co2_cam+I_limb_e_on_co+I_limb_dr
    I_limb_uvd=I_limb_e_on_co2_uvd

    I_limb_ratio=I_limb_cam/I_limb_uvd

    limbs.append((energy, I_limb_e_on_co2_uvd, I_limb_e_on_co2_cam, I_limb_e_on_co, I_limb_dr, I_limb_uvd, I_limb_cam, I_limb_ratio))




# plot ratio of CAM to UVD peak VER vs energy
plt.figure(figsize=(10,6))
energies, ratio_values = zip(*ratios)
plt.plot(energies, ratio_values, marker='o')
plt.xlabel('Electron Energy (eV)')
plt.ylabel('Ratio')
plt.title('CAM/UVD Ratio From Peak VER vs Monoenergetic Electron Energy')
plt.grid()
plt.show()


# plot intensities vs energy
plt.figure(figsize=(10,6))
energies, kR_e_on_co2_uvd_values, kR_e_on_co2_cam_values, kR_e_on_co_cam_values, kR_dr_values, kR_uvd_values, kR_cam_values, ratio_values = zip(*krs)
plt.plot(energies, kR_e_on_co2_uvd_values, marker='o', label='Electron impact on CO2 (UVD)')
plt.plot(energies, kR_e_on_co2_cam_values, marker='o', label='Electron impact on CO2 (CAM)')
plt.plot(energies, kR_e_on_co_cam_values, marker='o', label='Electron impact on CO (CAM)')
plt.plot(energies, kR_dr_values, marker='o', label='Dissociative Recombination (CAM)')
#plt.plot(energies, kR_uvd_values, marker='o', label='Total UVD Intensity')
#plt.plot(energies, kR_cam_values, marker='o', label='Total CAM Intensity')
plt.xlabel('Electron Energy (eV)')
plt.ylabel('Intensity (kR)')
plt.title('Emission Intensity vs Monoenergetic Electron Energy')
plt.legend()
plt.grid()
plt.show()

#plot total intensities
plt.figure(figsize=(10,3))
plt.loglog(energies, kR_uvd_values, marker='o', label='Total UVD Intensity')
plt.loglog(energies, kR_cam_values, marker='o', label='Total CAM Intensity')
plt.xlabel("Electron Energy (eV)")
plt.ylabel("Vertical Intensity (kR)")
plt.title("Intensity vs Energy")
plt.xlim(10,1000)
plt.ylim(.1,10)
plt.show()

#plot intensity ratios
plt.figure(figsize=(10,6))
energies,ratios=zip(*kR_ratios)
plt.plot(energies,ratios, marker='o')
plt.xlabel("Electron Energy (eV)")
plt.ylabel("Ratio")
plt.title("CAM/UVD Ratio from Intensity vs Monoenergetic Electron Energy")
plt.grid()
plt.show()

#plot limb intensities
energies, I_limb_e_on_co2_uvd_values, I_limb_e_on_co2_cam_values, I_limb_e_on_co_values, I_limb_dr_values, I_limb_uvd_values, I_limb_cam_values, I_limb_ratio_values= zip(*limbs)
plt.figure(figsize=(10,6))
plt.plot(energies, I_limb_e_on_co2_uvd_values, marker='o', label='Electron impact on CO2 (UVD)')
plt.plot(energies, I_limb_e_on_co2_cam_values, marker='o', label='Electron impact on CO2 (CAM)')
plt.plot(energies, I_limb_e_on_co_values, marker='o', label='Electron impact on CO (CAM)')
plt.plot(energies, I_limb_dr_values, marker='o', label='Dissociative Recombination (CAM)')
#plt.plot(energies, dr_avg_values, marker='o', label='Dissociative Recombination (CAM)')
plt.xlabel('Electron Energy (eV)')
plt.ylabel('Limb Intensity (kR)')
plt.title('Limb Intensity vs Monoenergetic Electron Energy')
plt.legend()
plt.grid()
plt.show()

#plot limb intensity ratios
plt.figure(figsize=(10,6))
energies, I_limb_e_on_co2_uvd_values, I_limb_e_on_co2_cam_values, I_limb_e_on_co_values, I_limb_dr_values, I_limb_uvd_values, I_limb_cam_values, I_limb_ratio_values = zip(*limbs)
plt.plot(energies, I_limb_ratio_values, marker='o')
plt.xlabel('Electron Energy (eV)')
plt.ylabel('Ratio')
plt.title('CAM/UVD Limb Intensity Ratio vs Monoenergetic Electron Energy')
plt.grid()
plt.show()

check_data=True
if check_data:
    #Cross sections
    plt.figure(figsize=(10,6))
    plt.plot(CO2_UVD_XS.keys(),CO2_UVD_XS.values(),label="e on CO2-UVD")
    #plt.plot(CO2_UVD_XS2.keys(),CO2_UVD_XS2.values(),label="Itikawa")
    plt.plot(CO2_CAM_XS.keys(),CO2_CAM_XS.values(),label="e on CO2-CAM")
    plt.plot(CO_CAM_XS.keys(),CO_CAM_XS.values(),label="e on CO-CAM")
    plt.legend()
    plt.xlabel("Energy (eV)")
    plt.ylabel("Cross Section (cm$^2$)")
    plt.title("Cross Section vs Energy")
    plt.show()

    #Densities
    plt.figure(figsize=(10,6))
    plt.semilogx(co2_density,alt_grid,label="CO2")
    plt.semilogx(co_density,alt_grid,label="CO")
    plt.semilogx(co2p_density,alt_grid,label="CO$_2^+$")
    plt.semilogx(e_density,alt_grid,label="e$_{th}$")
    plt.xlabel("Density (cm$^{-3}$)")
    plt.ylabel("Altitude (km)")
    plt.title("Particle Density vs Altitude")
    plt.legend()
    plt.grid()
    plt.show()

    #Flux
    plt.figure(figsize=(6,12))
    plt.semilogx(e_flux,alt_grid)
    plt.xlabel("Energetic Electron Flux ($cm^{-2}s^{-1}$)")
    plt.ylabel("Altitude (km)")
    plt.grid()
    plt.show()

    #Temp
    plt.figure(figsize=(6,12))
    plt.semilogx(e_temp,alt_grid)
    plt.xlabel("Temperature (k)")
    plt.ylabel("Altitude (km)")
    plt.title("Electron Temperature vs Altitude")
    plt.grid()
    plt.show()

    #Density ratio
    plt.figure(figsize=(10,6))
    plt.semilogx(co_density/co2_density, alt_grid)
    plt.xlabel("CO/CO$_2$ Ratio")
    plt.ylabel("Altitude (km)")
    plt.title("Altitude Variation of CO/CO$_2$ Ratio")
    plt.xlim(1e-4,1e3)
    plt.ylim(0,300)
    plt.grid()
    plt.show()