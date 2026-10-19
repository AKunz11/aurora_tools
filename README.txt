AURORA TOOLS
============

Tools for filtering Mars nightglow detections and exploring their spatial,
seasonal, spectral, and emission-ratio distributions. The main workflow reads a
master detection table, applies quality filters, converts locations to Mars-Sun
Orbital (MSO) coordinates, creates selected plots, and writes a filtered table.


QUICK START
-----------

1. Create and activate a virtual environment (PowerShell):

       py -m venv .venv
       .\.venv\Scripts\Activate.ps1

2. Install the Python dependencies:

       py -m pip install -r requirements.txt

3. Download the required NAIF SPICE kernels and place them in these folders:

       spice/LSK/naif0012.tls
       spice/PCK/pck00010.tpc
       spice/SPK/mar097.bsp

   The `spice/` directory is intentionally ignored by Git because the kernels
   are external data files.

4. Update the local paths before running anything:

   - In `main.py`, set `master_path` to the master detection CSV.
   - In `MSO_coords.py`, point the three `spice.furnsh(...)` calls at the
     downloaded kernels.
   - If using comparison mode, set `me_and_adrienne_path` in `main.py`.
   - Change any `D:/thesis_images/...` output paths in the plotting modules if
     those directories do not exist on your computer.

5. Run the main workflow:

       py main.py

   The filtered detections are written to `filtered_data.csv`. CSV files are
   ignored by Git because they are treated as local input or generated output.


SYSTEM REQUIREMENTS
-------------------

- Python with the packages pinned in `requirements.txt`
- The three SPICE kernels listed above
- A master detection CSV (not included in this repository)
- A LaTeX installation if `plt.rc('text', usetex=True)` remains enabled in
  `main.py` and `model2.py`
- Spectral `.npz` files for the coadded- and full-spectrum workflows


USING MAIN.PY
-------------

Configuration is currently done by editing the variables near the top of
`main.py`.

Selection settings:

- `orb_start`, `orb_stop`: inclusive lower and exclusive upper orbit bounds
- `key`: `All`, `Normal`, or `Anomalous`
- `min_sza`: minimum solar zenith angle
- `n_pix`: minimum number of contributing pixels
- `pearson_r`: minimum MUV Pearson correlation coefficient
- `coUVD`: CO Cameron/UVD ratio separating normal and anomalous detections
- `wl_dim`: expected spectral array length (`512` or `219`)

Optional switches:

- `consecutive_check`: keep orbits containing multiple qualifying scans
- `print_stuff`: print summary brightness and ratio statistics
- `isolate_orbits`: run the specialized orbit-selection workflow
- `orbit_compare`: merge detections with the external comparison table
- `remove_cutoff_bin`: remove the histogram bin surrounding the ratio cutoff

The plotting calls are grouped near the end of `main()`. Uncomment only the
plots you want to generate:

- `sza_hist(...)`: solar zenith angle distribution
- `plot_map(...)`: detections over the crustal magnetic-field map
- `latitude_hist(...)`: latitude distribution with a surface-area reference
- `plot_local_time(...)`: local-time distributions
- `nightside_dist(...)`: nightside locations in MSO coordinates
- `coadd(...)`: coadded spectra
- `plot_ratio(...)`: CO Cameron/UVD ratio distribution
- `alt_hist(...)`: normal-versus-anomalous altitude distributions
- `ratio_lat(...)`: emission ratio versus latitude
- `plot_coverage(...)`: date and solar-longitude coverage

The input table must include the columns used by the selected workflow. The
main filter expects at least:

    orbit_number, nick_number, scan, sza, count, pearson_r_muv,
    color_flag_muv, type, local_time, CO/CO2p, latitude, longitude,
    altitude, et

Some optional plots also use `date`, `solar_longitude`, `CO_radiance`, and
`CO2p_radiance`.


OTHER ANALYSIS SCRIPTS
----------------------

`big_spectra_plot.py`
    Loads per-orbit `.npz` spectra selected by a CSV table and creates a
    multi-page spectrum PDF. Update `csv_path`, `spectra_dir`, and `savepath`
    at the bottom of the file before running it.

`ks_test.py`
    Compares normal and anomalous SZA and latitude samples with two-sample
    Kolmogorov-Smirnov tests. Update `master_path`, then run:

        py ks_test.py

`n_distributions.py`
    Fits one- and two-Gaussian models to the CO Cameron/UVD ratio distribution
    and reports AIC/BIC values. Update `master_path`, then run:

        py n_distributions.py

`model2.py`
    Calculates volumetric emission-rate and intensity estimates for several
    monoenergetic electron energies. It reads atmospheric profiles from the
    ignored `data/` directory. See `model.txt` for the model assumptions, then
    run:

        py model2.py

`mag_field.py`
    Displays the crustal magnetic-field array by itself. Update the path in the
    final `plot_map(...)` call before running it.


MODULE GUIDE
------------

Core workflow:

- `main.py` - filters the master table and coordinates plot generation
- `MSO_coords.py` - converts Mars coordinates to the MSO frame
- `MSO.txt` - short definition of the MSO axes
- `coadded.py` - loads and coadds matching spectra

Plotting helpers:

- `altitude.py` - altitude distributions
- `coverage.py` - observation-date and solar-longitude coverage
- `latitude_hist.py` - latitude histogram and geometric reference
- `local_time.py` - local-time histograms
- `map.py` - detection locations over the magnetic-field map
- `nightside_dist.py` - nightside/MSO distribution plots
- `ratio_lat.py` - ratio versus latitude
- `ratios.py` - ratio histogram and Gaussian-mixture comparison helper
- `sza_hist.py` - SZA histogram and geometric reference

Supporting files:

- `bfield_smoothed.npy` - magnetic-field background used by `map.py`
- `model.txt` - notes and equations for `model2.py`
- `requirements.txt` - pinned Python dependencies
- `todo.txt` - development notes


DATA AND GENERATED FILES
------------------------

The repository intentionally ignores local environments, SPICE kernels, raw
data, CSV tables, figures, and generated spectrum PDFs. These files can be
large, machine-specific, or reproducible. See `.gitignore` for the complete
list.

If a file was already committed before an ignore rule was added, Git will
continue tracking it. To stop tracking such a file without deleting the local
copy, use:

    git rm --cached <path>


CURRENT LIMITATIONS
-------------------

- Several scripts still contain machine-specific absolute paths and must be
  configured locally.
- Some scripts execute their analysis immediately when imported; treat them as
  standalone scripts unless you refactor them behind a `main()` guard.
- The ignored input data and SPICE kernels are not downloaded automatically.
