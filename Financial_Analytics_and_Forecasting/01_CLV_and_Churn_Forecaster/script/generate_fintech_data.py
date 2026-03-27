import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

fake = Faker()
Faker.seed(202)
random.seed(202)
np.random.seed(202)

NUM_CUSTOMERS = 300
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

CITIES = ["Kuala Lumpur", "Puchong", "Petaling Jaya", "Penang", "Johor Bahru", "Shah Alam"]
ACQUISITION_CHANNELS = ["Organic Search", "Referral", "Social Media Ad", "In-Store Promo"]
TX_TYPES = ["Card Swipe", "Bill Payment", "Peer-to-Peer Transfer", "Top-Up"]

# --- Set up Paths ---
script_dir = Path(__file__).resolve().parent
data_dir = script_dir.parent / 'data'

# ==========================================
# 1. GENERATE CUSTOMER PROFILES
# ==========================================
print("Generating customer profiles...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    # Determine if this user will be a "Loyal" user or a "Churner"
    behavior_type = random.choices(["Loyal", "Churner", "Occasional"], weights=[40, 30, 30])[0]
    
    # Assign a random onboarding date
    onboard_date = START_DATE + timedelta(days=random.randint(0, 365))
    
    customers.append({
        "account_id": f"ACCT-{str(i).zfill(4)}",
        "city": random.choice(CITIES),
        "acquisition_channel": random.choice(ACQUISITION_CHANNELS),
        "onboarding_date": onboard_date,
        "behavior": behavior_type # Hidden label for our reference
    })

cust_df = pd.DataFrame(customers)
cust_df.drop(columns=["behavior"]).to_csv(data_dir / "customer_profiles.csv", index=False)

print(f"Customer profile with {len(cust_df)} records generated.")

# ==========================================
# 2. GENERATE TRANSACTION HISTORY
# ==========================================
print("Generating 12 months of transaction history...")
transactions = []

for cust in customers:
    current_date = cust["onboarding_date"]
    
    # Define how long the user remains active
    if cust["behavior"] == "Churner":
        # Churners stop using the app after 2 to 4 months
        active_days = random.randint(60, 120)
        end_active_date = current_date + timedelta(days=active_days)
        freq_days = random.randint(3, 10) # Transact every few days while active
    elif cust["behavior"] == "Loyal":
        end_active_date = END_DATE
        freq_days = random.randint(1, 4) # Highly frequent
    else: # Occasional
        end_active_date = END_DATE
        freq_days = random.randint(14, 30) # Infrequent

    # Generate transactions until their "end_active_date"
    while current_date < min(end_active_date, END_DATE):
        tx_type = random.choices(TX_TYPES, weights=[50, 20, 15, 15])[0]
        
        # Determine amount based on type
        if tx_type == "Top-Up":
            amt = round(random.uniform(100.0, 1000.0), 2)
        elif tx_type == "Bill Payment":
            amt = round(random.uniform(50.0, 300.0), 2)
        else: # Card or P2P
            amt = round(random.uniform(5.0, 150.0), 2)
            
        transactions.append({
            "transaction_id": fake.uuid4(),         # "transaction_id": fake.uuid4()[:8],
            "account_id": cust["account_id"],
            "timestamp": current_date + timedelta(hours=random.randint(8, 20)),
            "transaction_type": tx_type,
            "amount_myr": amt
        })
        
        # Advance time to the next transaction
        current_date += timedelta(days=freq_days + random.randint(-1, 2))

print(f"{len(transactions)} transaction logs created.")

# ==========================================
# 3. EXPORT
# ==========================================
print("Compiling and sorting ledger...")
tx_df = pd.DataFrame(transactions)
tx_df = tx_df.sort_values(by="timestamp").reset_index(drop=True)
tx_df.to_csv(data_dir / "transaction_history.csv", index=False)

print(f"Done! Generated {len(cust_df)} customers and {len(tx_df)} transactions.")