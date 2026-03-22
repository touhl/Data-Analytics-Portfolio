import pandas as pd
import numpy as np

# --- Helper Function: Vectorized Haversine Distance ---
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in kilometers between two sets of coordinates."""
    R = 6371.0 # Earth's radius in kilometers
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

# 1. Load the Data
print("Loading raw authentication logs...")
df = pd.read_csv("auth_logs_raw.csv")

# Ensure timestamp is a datetime object
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Initialize a new column for our detection labels
df['flagged_threat'] = "None"

# ==========================================
# RULE 1: BRUTE FORCE & CREDENTIAL STUFFING
# ==========================================
print("Scanning for Brute Force attacks...")

# We want to find IPs that have a high volume of failed logins.
# First, isolate the failed attempts
failed_logins = df[df['login_status'] == 'Failed'].copy()

# Count failed attempts per IP address
# In a production environment, you would use a rolling time window (e.g., 5 minutes)
# For this portfolio dataset, an aggregate count threshold works perfectly.
failed_counts = failed_logins.groupby('ip_address').size().reset_index(name='failure_count')

# Define our threshold (e.g., more than 15 failed attempts from a single IP is highly suspicious)
suspicious_ips = failed_counts[failed_counts['failure_count'] > 15]['ip_address'].tolist()

# Apply the flag to the main dataframe
df.loc[(df['ip_address'].isin(suspicious_ips)) & (df['login_status'] == 'Failed'), 'flagged_threat'] = "Brute Force"


# ==========================================
# RULE 2: IMPOSSIBLE TRAVEL (SESSION HIJACKING)
# ==========================================
print("Scanning for Impossible Travel anomalies...")

# Impossible travel only applies to SUCCESSFUL logins (someone actually got into the account)
success_logins = df[df['login_status'] == 'Success'].copy()

# Sort by User ID and Timestamp to look at consecutive logins
success_logins = success_logins.sort_values(by=['user_id', 'timestamp'])

# Shift data to compare current login to previous login
success_logins['prev_lat'] = success_logins.groupby('user_id')['latitude'].shift(1)
success_logins['prev_lon'] = success_logins.groupby('user_id')['longitude'].shift(1)
success_logins['prev_timestamp'] = success_logins.groupby('user_id')['timestamp'].shift(1)

# Calculate the time difference in hours between consecutive logins
success_logins['time_diff_hours'] = (success_logins['timestamp'] - success_logins['prev_timestamp']).dt.total_seconds() / 3600

# Calculate Physical Distance (in kilometers)
success_logins['distance_km'] = calculate_haversine_distance(
    success_logins['prev_lat'], success_logins['prev_lon'],
    success_logins['latitude'], success_logins['longitude']
)

# Calculate Velocity (Speed = Distance / Time)
# Avoid division by zero for simultaneous logins by adding a tiny fraction
success_logins['travel_speed_kmh'] = success_logins['distance_km'] / (success_logins['time_diff_hours'] + 0.0001)


# The Detection Logic: Faster than a commercial jet?
# Commercial jets fly at ~900 km/h. Let's use 1000 km/h as our impossible threshold.
impossible_travel_mask = (
    (success_logins['prev_lat'].notna()) & 
    (success_logins['travel_speed_kmh'] > 1000)
)


# Get the index of the flagged rows to update the main dataframe
flagged_indices = success_logins[impossible_travel_mask].index
df.loc[flagged_indices, 'flagged_threat'] = "Impossible Travel"

# ==========================================
# EXPORT RESULTS
# ==========================================
print("Exporting flagged dataset for visualization...")

# Let's see a quick summary of what we caught
print("\n--- Threat Detection Summary ---")
print(df['flagged_threat'].value_counts())
print("--------------------------------\n")

# Save the processed data for Tableau
df.to_csv("auth_logs_flagged.csv", index=False)
print("Saved to 'auth_logs_flagged.csv'. Ready for dashboarding!")