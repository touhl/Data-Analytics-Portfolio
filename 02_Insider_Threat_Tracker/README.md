# 🕵️‍♂️ Insider Threat & Data Loss Prevention (DLP) Engine

**Tech Stack:** `Python` `Pandas` `NumPy` `Statistical Modeling (MAD)` `Faker`

## 📋 Executive Summary
Insider threats—whether malicious data exfiltration or compromised internal accounts—are notoriously difficult to detect because the actors already possess legitimate access. This project simulates an enterprise Data Loss Prevention (DLP) environment. It correlates human resources metadata with digital access logs to detect contextual and statistical anomalies in employee behavior.

The detection engine flags two primary risk vectors:
1. **The Midnight Exfiltration:** Massive, unauthorized data downloads occurring strictly outside an employee's authorized working hours or departmental scope.
2. **The "Slow Leak":** Gradual data exfiltration detected via advanced statistical volume anomalies.

## 🏗️ Architecture & Methodology

### 1. Relational Data Engineering (`generate_insider_data.py`)
To mimic a true corporate architecture, I generated two synthetic, relational datasets:
* **HR Roster (`hr_roster.csv`):** Contains employee metadata, including department, role, risk tier, and authorized shift hours.
* **System Access Logs (`system_access_logs.csv`):** A 1 year log of all digital interactions, intentionally injected with hidden, highly realistic data theft scenarios.

### 2. Contextual Threat Detection (`detect_insider_threats.py`)
Raw event logs lack the context needed for IAM (Identity and Access Management) security. The detection engine merges the event data with the HR metadata to establish dynamic behavioral baselines.

* **Handling Skewed Network Traffic (Robust Z-Score):** Initially, a standard Z-Score was considered for volume anomaly detection. However, network traffic and file downloads are heavily right-skewed (non-Gaussian). Massive outlier downloads "poison" the baseline, inflating the mean and standard deviation, which causes actual data leaks to slip under the radar. 
* **The Solution:** Implemented a **Robust Z-Score** utilizing the **Median Absolute Deviation (MAD)**. By centering the logic around the median rather than the mean, the engine effectively resists baseline poisoning and accurately flags "slow leak" exfiltration without triggering false positives.

## 🚀 How to Run the Project

1. Clone the repository and navigate to the project folder.
2. Install dependencies:
   ```bash
   pip install pandas numpy faker
3. Generate the HR roster and access logs:
   ```bash
   python scripts/generate_insider_data.py
4. Run the contextual detection engine:
   ```bash
   python scripts/detect_insider_threats.py
5. Use insider_threat_flagged.csv in dashboard to visualise results

---
*Created by Tou Hui Ling - [Let's connect on LinkedIn](https://www.linkedin.com/in/huilingtou/)*