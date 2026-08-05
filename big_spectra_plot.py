import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def orbit_str(orbit):
    """Convert orbit number to file format, e.g. 4567 -> 04567."""
    orbit = int(orbit)
    return f"{orbit:05d}" if orbit < 10000 else str(orbit)


def load_spectra_for_orbits(
    csv_path,
    spectra_dir,
    orbit_col="orbit_number",
    scan_col=None,
    max_orbits=None
):
    df = pd.read_csv(csv_path)


    # Explicit filter
    df = df[
        (df['pearson_r_muv'] >= 0.6) & (df['CO/CO2p'] > 0) & (df['sza'] >= 105) & (df['type'] != 'NON-DET') & (df['type'] != 'NONE') & (df['count'] >= 6)
    ]

    # Anomalous Filter
    df = df[(df['CO/CO2p'] >= 12.7)]

    # Normal Filter
    #df = df[(df['CO/CO2p'] < 12.7)]

    # Optional orbit range
    df = df[(df[orbit_col] >= 400) & (df[orbit_col] < 15500)]

    if max_orbits is not None:
        df = df.head(max_orbits)

    print(f"Rows after filtering: {len(df)}")
    print(df[["nick_number", orbit_col]].head())

    all_spectra = []

    for _, row in df.iterrows():
        orbit = int(row[orbit_col])
        orbit_s = orbit_str(orbit)

        file_path = os.path.join(
            spectra_dir,
            f"orbit{orbit_s}_spectra.npz"
        )

        if not os.path.exists(file_path):
            print(f"Missing: {file_path}")
            continue

        data = np.load(file_path, allow_pickle=True)
        items = data["items"]

        # If scan_col is given, only load that scan
        if scan_col is not None:
            target_scan = int(row[scan_col])

            for spec in items:
                if int(spec["scan"]) == target_scan:
                    all_spectra.append(spec)
                    break

        # Otherwise load all scans from filtered orbits
        else:
            all_spectra.extend(items)

    print(f"Loaded {len(all_spectra)} spectra")
    return all_spectra, df


def is_valid_spectrum(spec):
    """Check that a spectrum has usable wavelength and background arrays."""

    if "wavelength_nm" not in spec or "background_kR" not in spec:
        return False

    wl = np.asarray(spec["wavelength_nm"])
    bg = np.asarray(spec["background_kR"])

    if len(wl) != len(bg):
        return False

    if np.all(np.isnan(bg)):
        return False

    return True


def plot_spectra_pdf(
    spectra,
    savepath,
    data_csv,
    ncols=5,
    nrows=4,
    smooth=None,
    title="Spectra"
):
    """
    Save spectra as a multi-page PDF.
    """

    # Open data csv for extra info
    df = data_csv.copy()

    # Remove bad spectra
    spectra = [s for s in spectra if is_valid_spectrum(s)]

    if len(spectra) == 0:
        raise ValueError("No valid spectra found.")

    plots_per_page = ncols * nrows

    with PdfPages(savepath) as pdf:

        # Loop over pages
        for start in range(0, len(spectra), plots_per_page):

            subset = spectra[start:start + plots_per_page]

            fig, axes = plt.subplots(
                nrows,
                ncols,
                figsize=(4 * ncols, 2.5 * nrows),
                squeeze=False
            )

            axes = axes.flatten()

            # Plot each spectrum
            for ax, spec in zip(axes, subset):

                wl = np.asarray(spec["wavelength_nm"])
                bg = np.asarray(spec["background_kR"])

                if smooth is not None:
                    from scipy.ndimage import uniform_filter1d
                    bg = uniform_filter1d(bg, size=smooth)

                ax.plot(wl, bg, lw=0.8, color="black")

                fit = spec.get("aurora_fit_kR", None)
                if fit is not None:
                    ax.plot(wl, fit, lw=0.8, ls="--", color="red")

                ax.axvline(190, ls=":", lw=0.5)
                ax.axvline(246, ls=":", lw=0.5)

                # Get L_s at spectrums orbit from dataframe
                orbit = spec.get('orbit')
                if orbit is not None:
                    orbit_data = df[df['orbit_number'] == orbit]
                    if not orbit_data.empty:
                        L_s = orbit_data['solar_longitude'].iloc[0]
                    else:
                        L_s = np.nan
                else:
                    L_s = np.nan

                label = (
                    f"Orbit {spec.get('orbit')}\n"
                    f"Scan {spec.get('scan')}\n"
                    f"R = {abs(spec.get('pearson_r', np.nan)):.2f}\n"
                    f"N pix = {spec.get('n_pixels', np.nan)}\n"
                    f"Ratio = {spec.get('co_average_kR') / spec.get('co2p_average_kR', 1):.2f}\n"
                    f"SZA = {spec.get('sza_deg', np.nan):.1f}°\n"
                    f"L_s = {L_s:.1f}°"
                )

                ax.text(
                    0.98,
                    0.95,
                    label,
                    transform=ax.transAxes,
                    ha="right",
                    va="top",
                    fontsize=6
                )

                ax.set_xticks([])
                ax.set_yticks([])

            # Turn off unused axes
            for ax in axes[len(subset):]:
                ax.axis("off")

            page_num = start // plots_per_page + 1

            fig.suptitle(
                f"{title} — Page {page_num}",
                fontsize=16,
                fontweight="bold"
            )

            fig.tight_layout()

            # Save current page
            pdf.savefig(fig)

            plt.close(fig)

    print(f"Saved PDF to: {savepath}")


# =====================
# Run everything here
# =====================

csv_path = "D:/nightglow_tables/master.csv"
spectra_dir = "D:/nightglow/spectra_out"
savepath = "D:/nightglow_tools/sample_spectra_grid.pdf"

spectra, df = load_spectra_for_orbits(
    csv_path=csv_path,
    spectra_dir=spectra_dir,
    orbit_col="orbit_number",
    scan_col="scan"
)

plot_spectra_pdf(
    spectra=spectra,
    savepath=savepath,
    data_csv=df,
    ncols=5,
    nrows=8,
    smooth=3,
    title="Anomalous Spectra, Verified"
)

plt.show()