import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pyplot as plt
import numpy as np

def alt_hist(data, n_bins=10):
    anoms   = data[data['CO/CO2p'] >= 12.7]
    normals = data[data['CO/CO2p'] < 12.7]

    all_alt = data['altitude'].to_numpy()

    # --- Shared bins (n_bins bins => n_bins+1 edges)
    bins = np.linspace(np.nanmin(all_alt), np.nanmax(all_alt), n_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    # --- Counts for error bars and scaling
    h_anom, _ = np.histogram(anoms['altitude'], bins=bins)
    h_norm, _ = np.histogram(normals['altitude'], bins=bins)

    # Colors (readable overlap)
    anom_color = '#2a9d8f'  # teal
    norm_color = '#7b2cbf'  # purple

    # --- Figure one
    plt.figure(figsize=(10,6))

    # =========================
    # Panel 1: Raw counts
    # =========================
    plt.hist(
        anoms['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=anom_color, alpha=0.9,
        label=f'Anomalous'
    )
    plt.hist(
        normals['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=norm_color, alpha=0.9,
        label=f'Normal'
    )

    # Poisson errors in counts: sqrt(N)
    plt.errorbar(
        h_anom, bin_centers, xerr=np.sqrt(h_anom),
        fmt='o', ms=4, color=anom_color, alpha=0.6
    )
    plt.errorbar(
        h_norm, bin_centers, xerr=np.sqrt(h_norm),
        fmt='o', ms=4, color=norm_color, alpha=0.6
    )

    plt.xlabel('Counts')
    plt.ylabel('Altitude (km)')
    plt.title('Altitude Distribution (Raw Counts)')
    plt.legend()

    # =========================
    # Panel 2: Total events scaling
    # Both populations contain the same number of events, so it removes differences based on sample size.
    # =========================
    plt.figure(figsize=(10, 6))
    # Counts of events
    N_anom = h_anom.sum()
    N_norm = h_norm.sum()
    
    # Guard against empty groups
    if N_anom == 0 or N_norm == 0:
        plt.text(
            0.5, 0.5,
            "One group has zero events; can't do equal-total scaling.",
            ha='center', va='center', transform=plt.gca().transAxes
        )
        plt.xlabel('Counts (scaled)')
        plt.ylabel('Altitude (km)')
        plt.title('Equal-Total Scaling')
        plt.show()
        return

    scale = max(N_anom, N_norm) #Choose larger total for scaling

    # Scaled bin counts (points), one histogram should remain the same as raw counts
    h_anom_scaled = h_anom * scale / N_anom
    h_norm_scaled = h_norm * scale / N_norm

    # Correct Poisson errors in scaled units
    err_anom_scaled = np.sqrt(h_anom) * scale / N_anom
    err_norm_scaled = np.sqrt(h_norm) * scale / N_norm

    # Use weights so histogram is ALSO in scaled-count units
    w_anom = np.full(len(anoms), scale / N_anom)
    w_norm = np.full(len(normals), scale / N_norm)

    plt.hist(
        anoms['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=anom_color, alpha=0.9,
        weights=w_anom, label=f'Anomalous'
    )
    plt.hist(
        normals['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=norm_color, alpha=0.9,
        weights=w_norm, label=f'Normal'
    )

    plt.errorbar(
        h_anom_scaled, bin_centers, xerr=err_anom_scaled,
        fmt='o', ms=4, color=anom_color, alpha=0.6
    )
    plt.errorbar(
        h_norm_scaled, bin_centers, xerr=err_norm_scaled,
        fmt='o', ms=4, color=norm_color, alpha=0.6
    )

    plt.xlabel('Counts (scaled to same total)')
    plt.ylabel('Altitude (km)')
    plt.title('Altitude Distribution (Equal-Total Scaling)')
    plt.legend()
    plt.show()

    
    # =========================
    # Panel 3: Max normalization
    # Each distribution scaled so its peak = 1
    # =========================
    plt.figure(figsize=(10, 6))
    # Avoid division by zero
    max_anom = np.max(h_anom) if np.max(h_anom) > 0 else 1
    max_norm = np.max(h_norm) if np.max(h_norm) > 0 else 1

    h_anom_max = h_anom / max_anom
    h_norm_max = h_norm / max_norm

    # Error propagation: sqrt(N) / max
    err_anom_max = np.sqrt(h_anom) / max_anom
    err_norm_max = np.sqrt(h_norm) / max_norm

    # Weights for histogram scaling
    w_anom_max = np.full(len(anoms), 1 / max_anom)
    w_norm_max = np.full(len(normals), 1 / max_norm)

    plt.hist(
        anoms['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=anom_color, alpha=0.9,
        weights=w_anom_max, label='Anomalous (max = 1)'
    )
    plt.hist(
        normals['altitude'], bins=bins, orientation='horizontal',
        histtype='step', linewidth=2.5, color=norm_color, alpha=0.9,
        weights=w_norm_max, label='Normal (max = 1)'
    )

    plt.errorbar(
        h_anom_max, bin_centers, xerr=err_anom_max,
        fmt='o', ms=4, color=anom_color, alpha=0.6
    )
    plt.errorbar(
        h_norm_max, bin_centers, xerr=err_norm_max,
        fmt='o', ms=4, color=norm_color, alpha=0.6
    )

    plt.xlabel('Normalized Counts (max = 1)')
    plt.ylabel('Altitude (km)')
    plt.title('Altitude Distribution (Max-Normalized)')
    plt.legend()
    plt.show()
    return