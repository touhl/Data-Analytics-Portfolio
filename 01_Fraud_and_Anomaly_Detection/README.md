# 🛡️ Account Takeover (ATO) & Bot Detection Engine

**Tech Stack:** `Python` `Pandas` `Faker` `Geospatial Analysis`

## 📋 Executive Summary
Compromised credentials and brute-force bot attacks are leading causes of data breaches. This project simulates a Security Operations Center (SOC) environment by engineering a detection pipeline that ingests raw web server authentication logs, identifies malicious behavior, and visualizes threats for security analysts. 

The detection engine specifically targets two major threat vectors:
1. **Credential Stuffing / Brute Force Attacks:** High-velocity authentication failures from a single origin.
2. **Session Hijacking (Impossible Travel):** Successful logins occurring from geographically distant locations within a physically impossible timeframe.

## 🏗️ Architecture & Methodology

### 1. Data Generation (`generate_auth_logs.py`)
To mimic a real-world enterprise environment without exposing proprietary PII, I built a Python script using the `Faker` library to generate a realistic synthetic dataset of 2,000+ authentication logs. 
* Includes IP addresses, exact lat/lon coordinates, user agents, and timestamps.
* Intentionally injects hidden "Brute Force" and "Impossible Travel" attack patterns to test the detection logic.
* *Note: In a production environment, IP coordinates would be derived via a Data Enrichment ETL step using a GeoIP database like MaxMind.*

### 2. Threat Detection Engine (`detect_anomalies.py`)
Built a rule-based detection engine using `Pandas` to process the raw logs and flag anomalies. 
* **Velocity-Based Geographic Analysis:** Implemented the **Haversine formula** to calculate the physical distance between consecutive user logins. By dividing the distance by the time delta, the engine calculates the required "travel velocity." If the required speed exceeds commercial airline capabilities (>1000 km/h), the session is flagged as hijacked.
* **Rolling Thresholds:** Aggregated authentication failures to identify high-frequency bot behavior bypassing standard rate limits.

## 🚀 How to Run the Project

1. Clone the repository and navigate to the project folder.
2. Install the required dependencies:
   ```bash
   pip install pandas faker numpy