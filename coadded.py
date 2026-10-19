import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def coadd(data, key, wl_dim=512, spectra_root="E:/nightglow/spectra_out"):
    bg = np.zeros(wl_dim, dtype=float)
    spectra_counts = 0
    wl = None

    # --- robust row iteration (works for pandas DF or list of dicts) ---
    if hasattr(data, "iterrows"):  # pandas DataFrame
        row_iter = (row for _, row in data.iterrows())
    else:  # list/array of dict-like rows
        row_iter = iter(data)

    for row in row_iter:
        # Your printout earlier shows 'orbit' not 'orbit_number' inside spectra items,
        # but here you're iterating some external table, so keep your column names:
        o = int(row["orbit_number"])
        s = int(row["scan"])  # currently unused, but kept if you need it later
        
        # Spectra are grouped into folders named for the first orbit in each
        # 100-orbit block: e.g. orbit 2457 is in ``02400``.
        block_start = (o // 100) * 100
        spectra_path = (
            Path(spectra_root)
            / f"{block_start:05d}"
            / f"orbit{o:05d}_spectra.npz"
        )
        try:
            spectra_data = np.load(spectra_path, allow_pickle=True)
        except FileNotFoundError:
            print(f"Spectra file not found: {spectra_path}")
            continue
        items = spectra_data["items"]

        # keep only items with correct wavelength dimension
        if key == 'Anomalous':
            good = [it for it in items if (it["background_kR"].size == wl_dim and it["scan"] == s and it['flag']==1 and (it['co_average_kR']/it['co2p_average_kR']) >= 12.7)]
        elif key == 'Normal':
            good = [it for it in items if (it["background_kR"].size == wl_dim and it["scan"] == s and it['flag']==1 and ((it['co_average_kR']/it['co2p_average_kR']) < 12.7))]
        else:  # key == 'All'
            good = [it for it in items if (it["background_kR"].size == wl_dim and it["scan"] == s and it['flag']==1)]

        if not good:
            continue

        # set wavelength grid once (from first good spectrum)
        if wl is None:
            wl = good[0]["wavelength_nm"]

        # elementwise sum across spectra (coadd), ignoring NaNs
        stack = np.stack([it["background_kR"] for it in good], axis=0)  # shape (n_good, wl_dim)
        bg += np.nansum(stack, axis=0)

        spectra_counts += len(good)

    if wl is None:
        raise ValueError(f"No spectra found with background_kR.size == {wl_dim}")

    fig, ax=plt.figure(), plt.axes()
    plt.plot(wl, bg)
    plt.xlabel("Wavelength (nm)")
    plt.title(f"Coadded Background Spectra - {key} - n={spectra_counts}")
    ax.axes.get_yaxis().set_visible(False)
    plt.savefig(f'D:/thesis_images/coadd_{key}.png', dpi=300)
    plt.show()

    return wl, bg
