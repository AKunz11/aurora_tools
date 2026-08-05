NIGHTGLOW TOOLS (Should be named aurora tools frankly)
Alexander Kunz


Important steps:
1. Install requirements
    pip install -r requirements.txt

2. Install spice kernels
    LSK
        naif0012.tls
    PCK
        pck00010.tpc
    SPK
        mar097.bsp

The only somewhat important files are outlined below

=======================================================================================================================================================
main.py

This is the function where just about all of the plotting is run.

Key parameters
orb_start: Start of orbit range
orb_stop: The stop
key: Whether we look at normal, anomalous, or all detections
consecutive_check: Only use orbits containing detections in neighboring scans
print_stuff: Whether u want to read annoying text
isolate_orbits: If we want to use orbits used in previous study by Adrienne Pickerill
orbit_compare: If we want to use orbits that I have AND that Adrienne used
remove_cutoff_bin: If we want to see what happens around the 12.7 cutoff
min_sza: minimum solar zenith angle of a detection
n_pix: minimum number of pixels in a detection
pearson_r: Pearson correlation coefficient
coUVD: The cutoff from normal->anomalous
wl_dim: Dimensions of the l1b file, usually use 512 or 219

Usage:
Plotting starts at line 202
(Just uncomment the plotting functions you want with each run)

sza_hist: Plots the SZA distribution for detections
plot_map: Plots the detection locations on the crustal magnetic field map
latitude_hist: distribution of latitudes
plot_local_time: distribution of local times
nightside_dist: Plots locations of detections on nightside using MSO coords
coadd: Coadded spectra for all the detections
plot_ratio: plots distribution of the CO Cameron / UVD 
alt_hist: Side-by-side comparison of altitude distributions
ratio_lat: 
plot_coverage: Shows orbit range and solar longitudes covered by data selection

Returns a "filtered_data.csv" containing good stuff

=======================================================================================================================================================
Multiple Guassian fit test
n_distributions.py

Used to check if the ratio data fit more than one distribution
Currently only works for 1 or 2 Gaussians, but math was derived by hand
If you want 3+, just use a premade library

=======================================================================================================================================================
Kolmogorov-Smirnov (KS) test
ks_test.py

Runs a KS test to check if data prefers a one-distribution or a two-distribution fit

=======================================================================================================================================================
Volumetric Emission Rate (VER) models
model2.py

Details in model.txt

Calculates and plots VER for the main reactions
Calculates and plots limb intensity
if check_data==True, plots the cross sections, electron flux, densities, electron temperatures

=======================================================================================================================================================
Big Spectra Plot
big_spectra_plot.py

Plots the spectra for all of the detections
Change the filters at lines 31, 34 to switch between normal and anomalous
Update directories at 217-219

=======================================================================================================================================================

Those are the big ticket items.
There are a few random python files that make some tables and stuff but pretty unnecessary
Also, I skipped the plotting functions used in main.py because I dont want to do all that



