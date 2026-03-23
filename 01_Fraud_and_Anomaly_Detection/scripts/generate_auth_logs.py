import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_USERS = 2000
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2024, 12, 31)

# We define a "Home" location to baseline normal traffic (Kuala Lumpur coordinates)
HOME_LAT = 3.1390
HOME_LON = 101.6869
HOME_CITY = "Kuala Lumpur"
HOME_COUNTRY = "Malaysia"

# 1. Create Normal Users
users = []
for i in range(1, NUM_USERS + 1):
    users.append({
        "user_id": f"USR-{str(i).zfill(4)}",
        "home_ip": fake.ipv4(),
        "user_agent": fake.user_agent()
    })

print(f"{len(users)} normal users generated.")

logs = []

# 2. Generate Normal Traffic
print("Generating normal traffic baseline...")
current_time = START_DATE
while current_time < END_DATE:
    user = random.choice(users)
    
    # 90% chance they login from home, 10% from elsewhere
    if random.random() < 0.90:
        ip = user["home_ip"]
        ua = user["user_agent"]
        lat, lon, city, country = HOME_LAT, HOME_LON, HOME_CITY, HOME_COUNTRY
    else:
        ip = fake.ipv4()
        ua = fake.user_agent()
        # Grab realistic geographic data
        location = fake.location_on_land() 
        lat, lon, city, country = location[0], location[1], location[2], location[3]
        
    status = "Success" if random.random() < 0.95 else "Failed"
    
    logs.append({
        "timestamp": current_time,
        "user_id": user["user_id"],
        "ip_address": ip,
        "latitude": float(lat),
        "longitude": float(lon),
        "country": country,
        "city": city,
        "user_agent": ua,
        "login_status": status,
        "threat_type": "None"
    })
    
    current_time += timedelta(minutes=random.randint(1, 60))

subtotal = len(logs)
print(f"{subtotal} normal traffic logs generated.")

# 3. Inject Brute Force Attack
print("Injecting Brute Force attacks...")
target_user = users[10]["user_id"]
attacker_ip = fake.ipv4()
attack_time = START_DATE + timedelta(days=2, hours=14)

for _ in range(35):
    logs.append({
        "timestamp": attack_time,
        "user_id": target_user,
        "ip_address": attacker_ip,
        "latitude": 55.7558,   # Moscow Lat
        "longitude": 37.6173,  # Moscow Lon
        "country": "Russia",
        "city": "Moscow",
        "user_agent": "python-requests/2.26.0",
        "login_status": "Failed",
        "threat_type": "Brute Force"
    })
    attack_time += timedelta(seconds=random.randint(2, 5))

brute_subtotal = len(logs) - subtotal
print(f"{brute_subtotal} Brute Force Attack logs injected.")

subtotal = len(logs)

# 4. Inject Impossible Travel
print("Injecting Impossible Travel anomaly...")
victim_user = users[50]["user_id"]
travel_time = START_DATE + timedelta(days=4, hours=9)

# Legitimate login
logs.append({
    "timestamp": travel_time,
    "user_id": victim_user,
    "ip_address": users[50]["home_ip"],
    "latitude": HOME_LAT,
    "longitude": HOME_LON,
    "country": HOME_COUNTRY,
    "city": HOME_CITY,
    "user_agent": users[50]["user_agent"],
    "login_status": "Success",
    "threat_type": "None"
})

# Suspicious login 10 minutes later
logs.append({
    "timestamp": travel_time + timedelta(minutes=10),
    "user_id": victim_user,
    "ip_address": fake.ipv4(),
    "latitude": 52.3676,   # Amsterdam Lat
    "longitude": 4.9041,   # Amsterdam Lon
    "country": "Netherlands",
    "city": "Amsterdam",
    "user_agent": fake.user_agent(),
    "login_status": "Success",
    "threat_type": "Impossible Travel"
})

impossible_subtotal = len(logs) - subtotal
print(f"{impossible_subtotal} Impossible Travel logs injected.")


# 5. Export
print("Compiling dataset...")
df = pd.DataFrame(logs)
df = df.sort_values(by="timestamp").reset_index(drop=True)

df.drop(columns=["threat_type"]).to_csv(r"01_Fraud_and_Anomaly_Detection\data\auth_logs_raw.csv", index=False)
df.to_csv(r"01_Fraud_and_Anomaly_Detection\data\auth_logs_labeled_master.csv", index=False)

print(f"Done! Generated {len(df)} authentication logs.")