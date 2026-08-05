import pandas as pd
import numpy as np


# Open CSVs
adriennes = pd.read_csv('adrienne_orbits.csv')
mine = pd.read_csv('my_orbits.csv')
rejects = pd.read_csv('visual_inspection.csv')


# Restrict to important headers only
adriennes = adriennes[['orbit_number', 'nick_number']]
mine = mine[['orbit_number', 'nick_number']]
rejects = rejects[['orbit_number', 'nick_number', 'type']]


# Clean nick_number formatting
for df in [adriennes, mine, rejects]:
    df['nick_number'] = df['nick_number'].astype(str).str.strip()


# Clean type formatting
rejects['type'] = rejects['type'].astype(str).str.strip()


# Classification columns
adriennes['hers'] = 'Y'
adriennes['mine'] = 'N'
adriennes['have_data'] = 'N'
adriennes['good_data'] = 'NA'

mine['hers'] = 'N'
mine['mine'] = 'Y'
mine['have_data'] = 'Y'
mine['good_data'] = 'Y'


# Mark visual rejects / non-detections as bad data
bad_nicks = rejects[
    rejects['type'].isin(['NON_DET', 'NON-DET'])
]['nick_number']

mine.loc[
    mine['nick_number'].isin(bad_nicks),
    'good_data'
] = 'N'


# Combine Adrienne + mine
combined = pd.concat([adriennes, mine], ignore_index=True)


# Keep one row per nick_number
combined = combined.groupby('nick_number', as_index=False).agg({
    'orbit_number': 'first',

    # Y if either source has it
    'hers': lambda x: 'Y' if 'Y' in x.values else 'N',
    'mine': lambda x: 'Y' if 'Y' in x.values else 'N',
    'have_data': lambda x: 'Y' if 'Y' in x.values else 'N',

    # If I have it, report whether it is good.
    # If only Adrienne has it, keep NA.
    'good_data': lambda x: (
        'N' if 'N' in x.values
        else 'Y' if 'Y' in x.values
        else 'NA'
    )
})


# Save CSV
combined.to_csv('combined_orbits.csv', index=False)


# Print metrics
total_scans = len(combined)

hers_scans = len(combined[combined['hers'] == 'Y'])
mine_scans = len(combined[combined['mine'] == 'Y'])

have_data_scans = len(combined[combined['have_data'] == 'Y'])
unknown_data_scans = len(combined[combined['good_data'] == 'NA'])
good_data_scans = len(combined[combined['good_data'] == 'Y'])
bad_data_scans = len(combined[combined['good_data'] == 'N'])

both_scans = len(combined[
    (combined['hers'] == 'Y') &
    (combined['mine'] == 'Y')
])

hers_only_scans = len(combined[
    (combined['hers'] == 'Y') &
    (combined['mine'] == 'N')
])

mine_only_scans = len(combined[
    (combined['hers'] == 'N') &
    (combined['mine'] == 'Y')
])

both_good_scans = len(combined[
    (combined['hers'] == 'Y') &
    (combined['mine'] == 'Y') &
    (combined['good_data'] == 'Y')
])

hers_only_unknown_scans = len(combined[
    (combined['hers'] == 'Y') &
    (combined['mine'] == 'N') &
    (combined['good_data'] == 'NA')
])

mine_only_good_scans = len(combined[
    (combined['hers'] == 'N') &
    (combined['mine'] == 'Y') &
    (combined['good_data'] == 'Y')
])


print('====================================')
print(f"%%%%% Total scans: {total_scans} %%%%%")
print(f"Hers scans: {hers_scans}")
print(f"Hers scans I don't have: {hers_only_scans}")
print(f"Mine scans: {mine_scans}")
print(f"My scans she doesn't have: {mine_only_scans}")
print(f"Overlap scans: {both_scans}")
print('------------------------------------')
print(f"Have data: {have_data_scans}")
print(f"Good data: {good_data_scans}")
print(f"Bad data / NON_DET: {bad_data_scans}")
print(f"Unknown good_data / Adrienne only: {unknown_data_scans}")
print('------------------------------------')
print(f"Overlap good scans: {both_good_scans}")
print(f"Hers-only unknown scans: {hers_only_unknown_scans}")
print(f"Mine-only good scans: {mine_only_good_scans}")
print('====================================')