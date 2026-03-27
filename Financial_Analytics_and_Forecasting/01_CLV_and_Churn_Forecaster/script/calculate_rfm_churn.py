import pandas as pd
import numpy as np
from pathlib import Path

# --- Set up Paths ---
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / 'data'


print("Loading datasets...")
tx_df = pd.read_csv(data_dir /"transaction_history.csv")
cust_df = pd.read_csv(data_dir /"customer_profiles.csv")

# Ensure datetimes are properly formatted
tx_df['timestamp'] = pd.to_datetime(tx_df['timestamp'])
cust_df['onboarding_date'] = pd.to_datetime(cust_df['onboarding_date'])

# To simulate a real-time environment, we set "today" as the day after the last transaction in the dataset
analysis_date = tx_df['timestamp'].max() + pd.Timedelta(days=1)

# ==========================================
# 1. CALCULATE RFM METRICS
# ==========================================
print("Calculating Recency, Frequency, and Monetary (RFM) values...")
rfm = tx_df.groupby('account_id').agg({
    'timestamp': lambda x: (analysis_date - x.max()).days,  # Recency: Days since last transaction
    'transaction_id': 'count',                              # Frequency: Total number of transactions
    'amount_myr': 'sum'                                     # Monetary: Total Lifetime Value (CLV)
}).reset_index()

rfm.rename(columns={
    'timestamp': 'recency_days', 
    'transaction_id': 'frequency_count', 
    'amount_myr': 'lifetime_value_myr'
}, inplace=True)

# Merge back with the demographic data to get the full picture
df = pd.merge(rfm, cust_df, on='account_id', how='left')

# Calculate Account Age in days
df['account_age_days'] = (analysis_date - df['onboarding_date']).dt.days

# Calculate average transaction value
df['avg_transaction_value'] = df['lifetime_value_myr'] / df['frequency_count']

# ==========================================
# 2. CUSTOMER SEGMENTATION & CHURN SCORING
# ==========================================
print("Applying behavioral segmentation and churn risk scoring...")

# Initialize default segment
df['customer_segment'] = "Standard"

# Define the logical rules for segmentation
# 1. Champions: Top spenders, transact often, seen recently.
champions_mask = (df['lifetime_value_myr'] > df['lifetime_value_myr'].quantile(0.75)) & (df['recency_days'] <= 14)

# 2. At-Risk VIPs: Top spenders who haven't been seen in over a month (High Churn Risk!)
at_risk_vip_mask = (df['lifetime_value_myr'] > df['lifetime_value_myr'].quantile(0.75)) & (df['recency_days'] > 30) & (df['recency_days'] <= 90)

# 3. Churned: Anyone who hasn't transacted in 90+ days
churned_mask = df['recency_days'] > 90

# 4. New Active Users: Accounts less than 60 days old that have transacted recently
new_active_mask = (df['account_age_days'] < 60) & (df['recency_days'] <= 14)

# Apply segments
df.loc[champions_mask, 'customer_segment'] = "Champion"
df.loc[new_active_mask, 'customer_segment'] = "New Active"
df.loc[at_risk_vip_mask, 'customer_segment'] = "At-Risk VIP"
df.loc[churned_mask, 'customer_segment'] = "Churned"

# ==========================================
# EXPORT RESULTS
# ==========================================
print("\n--- Revenue Management Segmentation Summary ---")
print(df['customer_segment'].value_counts())
print("-----------------------------------------------\n")

# Save the master analytical dataset for analysis and reporting
output_path = data_dir / "rfm_analysis_master.csv"
df.to_csv(output_path, index=False)
print(f"Saved to '{output_path}'.")