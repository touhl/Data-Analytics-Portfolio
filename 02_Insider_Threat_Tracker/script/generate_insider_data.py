import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np

fake = Faker()
Faker.seed(101)
random.seed(101)
np.random.seed(101)

NUM_EMPLOYEES = 150
START_DATE = datetime(2024, 9, 1)
END_DATE = datetime(2024, 10, 1) # 30 days of logs

# ==========================================
# 1. GENERATE HR ROSTER
# ==========================================
print("Generating HR Roster...")
departments = {
    "Ground Operations": {"roles": ["Dispatcher", "Driver", "Hub Manager"], "shift": (6, 18)},
    "Warehouse": {"roles": ["Inventory Specialist", "Forklift Operator"], "shift": (8, 20)},
    "Finance": {"roles": ["Financial Analyst", "Payroll Manager"], "shift": (9, 17)},
    "IT": {"roles": ["System Admin", "Helpdesk"], "shift": (9, 17)}
}

hr_data = []
for i in range(1, NUM_EMPLOYEES + 1):
    dept_name = random.choice(list(departments.keys()))
    role = random.choice(departments[dept_name]["roles"])
    shift_start, shift_end = departments[dept_name]["shift"]
    
    hr_data.append({
        "employee_id": f"EMP-{str(i).zfill(4)}",
        "name": fake.name(),
        "department": dept_name,
        "role": role,
        "shift_start_hour": shift_start,
        "shift_end_hour": shift_end,
        "risk_tier": "Standard" if dept_name in ["Ground Operations", "Warehouse"] else "Elevated"
    })

hr_df = pd.DataFrame(hr_data)
hr_df.to_csv(r"02_Insider_Threat_Tracker\data\hr_roster.csv", index=False)

print(f"HR Roster with {len(hr_df)} employees generated.")

# ==========================================
# 2. GENERATE NORMAL ACCESS LOGS
# ==========================================
print("Generating 30 days of normal system access logs...")
systems = ["Inventory_DB", "Routing_Portal", "Customer_CRM", "Financial_Ledger", "HR_Portal"]
actions = ["View", "Query", "Download", "Export"]

logs = []
current_time = START_DATE

# Generate baseline traffic
while current_time < END_DATE:
    emp = random.choice(hr_data)
    
    # Is it during their shift? (Rough approximation)
    is_shift_hours = emp["shift_start_hour"] <= current_time.hour <= emp["shift_end_hour"]
    
    # 95% of activity happens during shift hours
    if (is_shift_hours and random.random() < 0.95) or (not is_shift_hours and random.random() < 0.05):
        
        # Ground/Warehouse rarely access Finance; Finance rarely accesses Routing
        if emp["department"] in ["Ground Operations", "Warehouse"]:
            sys = random.choices(systems, weights=[50, 40, 5, 1, 4])[0]
        elif emp["department"] == "Finance":
            sys = random.choices(systems, weights=[5, 1, 20, 70, 4])[0]
        else:
            sys = random.choice(systems)

        action = random.choices(actions, weights=[60, 30, 8, 2])[0]
        
        # Normal bytes transferred (View/Query = small, Download/Export = larger but under 50MB usually)
        if action in ["Download", "Export"]:
            bytes_transferred = int(np.random.normal(15000000, 5000000)) # ~15MB average
        else:
            bytes_transferred = int(np.random.normal(50000, 20000)) # ~50KB average
            
        logs.append({
            "timestamp": current_time,
            "employee_id": emp["employee_id"],
            "system_accessed": sys,
            "action": action,
            "bytes_transferred": abs(bytes_transferred)
        })
        
    current_time += timedelta(minutes=random.randint(2, 15))

subtotal = len(logs)
print(f"{subtotal} normal logs created.")

# ==========================================
# 3. INJECT INSIDER THREAT ANOMALIES
# ==========================================
print("Injecting Insider Threat scenarios...")

# Threat 1: The Midnight Data Exfiltration (Off-hours + Wrong System + Massive Download)
# Let's pick a Hub Manager (Ground Operations)
hub_managers = [e for e in hr_data if e["role"] == "Hub Manager"]
rogue_manager = hub_managers[0]
rogue_time = START_DATE + timedelta(days=14, hours=2) # 2:00 AM

print(f"  -> Threat 1 Injected: {rogue_manager['employee_id']} downloading CRM data at 2 AM.")
for _ in range(5): # 5 massive downloads in a row
    logs.append({
        "timestamp": rogue_time,
        "employee_id": rogue_manager["employee_id"],
        "system_accessed": "Customer_CRM", # Shouldn't be touching this heavily
        "action": "Export",
        "bytes_transferred": 2_500_000_000 # 2.5 GB per file!
    })
    rogue_time += timedelta(minutes=3)

# Threat 2: The "Slow Leak" (Volume Anomaly over days)
# Let's pick a Financial Analyst secretly exporting the ledger bit by bit
analysts = [e for e in hr_data if e["role"] == "Financial Analyst"]
leaker = analysts[0]
leak_time = START_DATE + timedelta(days=20, hours=10)

print(f"  -> Threat 2 Injected: {leaker['employee_id']} slowly leaking Financial Ledger data.")
for i in range(40): # 40 abnormal downloads spread across a few days
    logs.append({
        "timestamp": leak_time,
        "employee_id": leaker["employee_id"],
        "system_accessed": "Financial_Ledger",
        "action": "Download",
        "bytes_transferred": 850_000_000 # 850 MB (way above normal 15MB average)
    })
    leak_time += timedelta(hours=random.randint(1, 4))

insider_subtotal = len(logs) - subtotal
print(f"{insider_subtotal} Brute Force Attack logs injected.")

# ==========================================
# 4. EXPORT
# ==========================================
print("Compiling and exporting logs...")
logs_df = pd.DataFrame(logs)
logs_df = logs_df.sort_values(by="timestamp").reset_index(drop=True)

logs_df.to_csv(r"02_Insider_Threat_Tracker\data\system_access_logs.csv", index=False)
print(f"Done! Created HR Roster and {len(logs_df)} access logs.")