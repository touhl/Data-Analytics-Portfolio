import pandas as pd
import numpy as np

# 1. Load Data
print("Loading HR and Access Log data...")
hr_df = pd.read_csv(r"02_Insider_Threat_Tracker\data\hr_roster.csv")
logs_df = pd.read_csv(r"02_Insider_Threat_Tracker\data\system_access_logs.csv")
logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])

# 2. Contextual Data Merge (Feature Engineering)
# Bring the employee's role, department, and shift hours into the log data
df = pd.merge(logs_df, hr_df, on="employee_id", how="left")

# Extract the hour of the day for time-based rules
df['hour_of_day'] = df['timestamp'].dt.hour
df['flagged_threat'] = "None"

# ==========================================
# RULE 1: MIDNIGHT DATA EXFILTRATION
# ==========================================
print("Scanning for out-of-hours massive data exfiltration...")

# Identify actions occurring strictly outside the employee's authorized shift hours
out_of_hours_mask = (df['hour_of_day'] < df['shift_start_hour']) | (df['hour_of_day'] >= df['shift_end_hour'])

# Flag if it's a massive download/export (e.g., > 1 GB)
massive_download_mask = (df['action'].isin(['Download', 'Export'])) & (df['bytes_transferred'] > 1_000_000_000)

rule1_flags = out_of_hours_mask & massive_download_mask
df.loc[rule1_flags, 'flagged_threat'] = "Midnight Exfiltration"

# ==========================================
# RULE 2: THE "SLOW LEAK" (ROBUST Z-SCORE / MAD)
# ==========================================
print("Scanning for statistical volume anomalies using Robust Z-Score (MAD)...")

# Filter for download/export actions to build a baseline for each user
downloads = df[df['action'].isin(['Download', 'Export'])].copy()

# Calculate the Median for each user over their entire log history
user_medians = downloads.groupby('employee_id')['bytes_transferred'].median().reset_index()
user_medians.rename(columns={'bytes_transferred': 'median_bytes'}, inplace=True)

# Merge medians back to calculate absolute deviation
downloads = pd.merge(downloads, user_medians, on='employee_id', how='left')
downloads['abs_deviation'] = (downloads['bytes_transferred'] - downloads['median_bytes']).abs()

# Calculate the MAD (Median Absolute Deviation) for each user
user_mad = downloads.groupby('employee_id')['abs_deviation'].median().reset_index()
user_mad.rename(columns={'abs_deviation': 'mad_bytes'}, inplace=True)

# Merge MAD back to the downloads dataframe
downloads = pd.merge(downloads, user_mad, on='employee_id', how='left')

# Avoid division by zero for users with zero variance
downloads['mad_bytes'] = downloads['mad_bytes'].replace(0, 1_000_000_000)
downloads['mad_bytes'] = downloads['mad_bytes'].fillna(1_000_000_000) 

# Calculate the Robust Z-Score
downloads['robust_z_score'] = (0.6745 * (downloads['bytes_transferred'] - downloads['median_bytes'])) / downloads['mad_bytes']

# Detection Logic: Flag if Robust Z-Score is > 3.5 (Highly unusual)
slow_leak_mask = (
    (downloads['robust_z_score'] > 3.5) & 
    (downloads['bytes_transferred'] > 100_000_000) & # Require it to be a relatively large file
    (df['flagged_threat'] == "None") # Prevent overwriting other flags
)

# Update the main dataframe
flagged_indices = downloads[slow_leak_mask].index
df.loc[flagged_indices, 'flagged_threat'] = "Volume Anomaly (Slow Leak)"


# ==========================================
# EXPORT RESULTS
# ==========================================
print("\n--- Insider Threat Detection Summary ---")
print(df['flagged_threat'].value_counts())
print("----------------------------------------\n")

# Save the processed, enriched data for reporting
df.to_csv(r"02_Insider_Threat_Tracker\data\insider_threat_flagged.csv", index=False)
print("Saved to 'insider_threat_flagged.csv'.")