import pandas as pd

# Paths
master_path = r"D:/nightglow_tables/master.csv"
combined_path = r"D:/nightglow_tools/combined_orbits.csv"
output_path = r"D:/nightglow_tools/combined_orbits_with_data_ALL.csv"

# Read files
master = pd.read_csv(master_path)
combined = pd.read_csv(combined_path)

# Make nick_number merge-safe
master["nick_number"] = master["nick_number"].astype(float).round(2).map(lambda x: f"{x:.2f}")
combined["nick_number"] = combined["nick_number"].astype(float).round(2).map(lambda x: f"{x:.2f}")

# Avoid duplicate orbit_number columns if both files have it
if "orbit_number" in combined.columns and "orbit_number" in master.columns:
    master = master.drop(columns=["orbit_number"])

# Drop duplicate master rows per nick_number
master = master.drop_duplicates(subset=["nick_number"])

# Merge: keep every row from combined_orbits
merged = combined.merge(
    master,
    on="nick_number",
    how="left",
    suffixes=("", "_master")
)

# Optional: sort nicely
if "orbit_number" in merged.columns:
    merged = merged.sort_values(["orbit_number", "nick_number"])

# Restrict Pearson R
if "Pearson_R" in merged.columns:
    merged = merged[merged["pearson_r_muv"] >= 0.6]

# Save
merged.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
print(f"Rows in combined_orbits: {len(combined)}")
print(f"Rows in output: {len(merged)}")
print(f"Rows missing master data: {merged.isna().all(axis=1).sum()}")
print(f"Nick rows with no CO/CO2p data: {merged['CO/CO2p'].isna().sum() if 'CO/CO2p' in merged.columns else 'CO/CO2p column not found'}")