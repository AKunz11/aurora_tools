# Aurora Tools

Python tools for filtering Mars nightglow detections and exploring their spatial, seasonal, spectral, and emission-ratio distributions.

The main workflow reads a master detection table, applies configurable quality filters, converts locations into Mars–Sun Orbital (MSO) coordinates, creates selected plots, and exports a filtered table.

> [!IMPORTANT]
> This project currently uses local, machine-specific paths. Update the paths in the relevant scripts before running an analysis.

## Contents

- [Quick start](#quick-start)
- [Requirements](#requirements)
- [Main workflow](#main-workflow)
- [Input data](#input-data)
- [Analysis scripts](#analysis-scripts)
- [Project structure](#project-structure)
- [Data and generated files](#data-and-generated-files)
- [Known limitations](#known-limitations)

## Quick start

### 1. Create a virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

### 3. Add the SPICE kernels

Download the required [NAIF SPICE kernels](https://naif.jpl.nasa.gov/naif/data.html) and place them in the following structure:

```text
spice/
├── LSK/
│   └── naif0012.tls
├── PCK/
│   └── pck00010.tpc
└── SPK/
    └── mar097.bsp
```

The `spice/` directory is ignored by Git because these kernels are external data files.

### 4. Configure local paths

Before running the project:

1. Set `master_path` in `main.py` to the master detection CSV.
2. Keep the kernels in the `spice/` structure shown above. The project loads
   them relative to `MSO_coords.py`; when they are absent, the workflow skips
   only the MSO nightside plot and continues with the other plots.
3. If you use comparison mode, set `me_and_adrienne_path` in `main.py`.
4. Set `plot_save_dir` in `main.py` if you want a location other than
   `E:/alex_final_figs`.

### 5. Run the workflow

```powershell
py main.py
```

The workflow writes the selected detections to `filtered_data.csv`.

## Requirements

| Requirement | Purpose |
| --- | --- |
| Python and the packages in `requirements.txt` | Data processing, statistics, plotting, and coordinate conversion |
| NAIF SPICE kernels | Mars coordinate transformations |
| Master detection CSV | Primary analysis input; not included in the repository |
| LaTeX installation | Optional for the main workflow; still required by scripts such as `model2.py` that enable `usetex=True` |
| Spectral `.npz` files | Required for the coadded- and full-spectrum workflows |

## Main workflow

Configuration is handled by editing the variables near the top of `main.py`.

### Selection settings

| Variable | Description |
| --- | --- |
| `orb_start`, `orb_stop` | Inclusive lower and exclusive upper orbit bounds |
| `key` | Detection group: `All`, `Normal`, or `Anomalous` |
| `min_sza` | Minimum solar zenith angle |
| `n_pix` | Minimum number of contributing pixels |
| `pearson_r` | Minimum MUV Pearson correlation coefficient |
| `coUVD` | CO Cameron/UVD ratio separating normal and anomalous detections |
| `wl_dim` | Expected spectral-array length: `512` or `219` |

### Optional switches

| Variable | Effect |
| --- | --- |
| `consecutive_check` | Keeps orbits containing multiple qualifying scans |
| `print_stuff` | Prints summary brightness and ratio statistics |
| `isolate_orbits` | Runs the specialized orbit-selection workflow |
| `orbit_compare` | Merges detections with the external comparison table |
| `remove_cutoff_bin` | Removes the histogram bin surrounding the ratio cutoff |

### Plotting options

Plotting calls are grouped near the end of `main()`. Uncomment only the products you want to generate.

| Function | Output |
| --- | --- |
| `sza_hist(...)` | Solar zenith angle distribution |
| `plot_map(...)` | Detections over the crustal magnetic-field map |
| `latitude_hist(...)` | Latitude distribution with a surface-area reference |
| `plot_local_time(...)` | Local-time distributions |
| `nightside_dist(...)` | Nightside locations in MSO coordinates |
| `coadd(...)` | Coadded spectra |
| `plot_ratio(...)` | CO Cameron/UVD ratio distribution |
| `alt_hist(...)` | Normal-versus-anomalous altitude distributions |
| `ratio_lat(...)` | Emission ratio versus latitude |
| `plot_coverage(...)` | Date and solar-longitude coverage |

## Input data

The master table must contain the columns used by the selected workflow. The main filter expects at least:

```text
orbit_number, nick_number, scan, sza, count, pearson_r_muv,
color_flag_muv, type, local_time, CO/CO2p, latitude, longitude,
altitude, et
```

Some optional plots also use:

```text
date, solar_longitude, CO_radiance, CO2p_radiance
```

## Analysis scripts

### `big_spectra_plot.py`

Loads per-orbit `.npz` spectra selected by a CSV table and creates a multi-page spectrum PDF. Update `csv_path`, `spectra_dir`, and `savepath` at the bottom of the file before running it.

### `ks_test.py`

Compares normal and anomalous SZA and latitude samples using two-sample Kolmogorov–Smirnov tests. Update `master_path`, then run:

```powershell
py ks_test.py
```

### `n_distributions.py`

Fits one- and two-Gaussian models to the CO Cameron/UVD ratio distribution and reports AIC and BIC values. Update `master_path`, then run:

```powershell
py n_distributions.py
```

### `model2.py`

Calculates volumetric emission-rate and intensity estimates for several monoenergetic electron energies. It reads atmospheric profiles from the ignored `data/` directory. See `model.txt` for the model assumptions, then run:

```powershell
py model2.py
```

### `mag_field.py`

Displays the crustal magnetic-field array by itself. Update the path in the final `plot_map(...)` call before running it.

## Project structure

```text
aurora_tools/
├── main.py                 # Main filtering and plotting workflow
├── MSO_coords.py           # Mars-to-MSO coordinate conversion
├── coadded.py              # Spectrum loading and coaddition
├── altitude.py             # Altitude distributions
├── coverage.py             # Date and solar-longitude coverage
├── latitude_hist.py        # Latitude histogram
├── local_time.py           # Local-time histograms
├── map.py                  # Magnetic-field map overlay
├── nightside_dist.py       # Nightside/MSO distributions
├── ratio_lat.py            # Emission ratio versus latitude
├── ratios.py               # Ratio distribution helpers
├── sza_hist.py             # Solar zenith angle histogram
├── bfield_smoothed.npy     # Magnetic-field background data
├── requirements.txt        # Pinned Python dependencies
├── MSO.txt                 # Definition of the MSO axes
└── model.txt               # Emission-model notes and equations
```

## Data and generated files

Local environments, SPICE kernels, raw data, CSV tables, figures, and selected generated spectrum PDFs are intentionally ignored by Git. These files are large, machine-specific, or reproducible. See `.gitignore` for the complete list.

If a file was committed before an ignore rule was added, stop tracking it without deleting the local copy:

```powershell
git rm --cached <path>
```

## Known limitations

- Several scripts contain machine-specific absolute paths and require local configuration.
- Some scripts execute immediately when imported. Treat them as standalone scripts unless they are refactored behind a `main()` guard.
- Input data and SPICE kernels are not downloaded automatically.
