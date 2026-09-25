# Resumable & Resilient Web Extraction Pipeline

An enterprise-grade, queue-driven data collection pipeline designed with state persistence, polite rate limiting, graceful error handling, and manual CAPTCHA/login-wall intervention protocols.

This project was built as a system-design demonstration for crawling public directories safely and reliably without brute-forcing server protections or violating site terms.

---

## 🏗️ System Architecture

The pipeline relies on a **two-table state machine** architecture to guarantee that job progress is fully observable and instantly resumable across system restarts or network failures:

```
                  +-----------------------+
                  |  Crawl Queue (MySQL)  |
                  +-----------------------+
                              |
               +--------------+--------------+
               |                             |
      [Pending / Failed]               [Completed]
               |                             |
               v                             v
     +-------------------+         +-------------------+
     | Worker Loop Engine |         | Skip (Idempotent) |
     +-------------------+         +-------------------+
               |
    +----------+----------+
    |                     |
[Success]             [CAPTCHA / Block]
    |                     |
    v                     v
+------------+     +-------------------------------+
| Store Data |     | Pause Queue & Prompt Manual   |
| & Mark     |     | Verification                  |
| Completed  |     +-------------------------------+
+------------+
```

---

## ✨ Key Features

* **Instant Resumability**: Tracks task states (`pending`, `in_progress`, `completed`, `failed`, `captcha`) in MySQL. If interrupted mid-run, the worker skips finished records and resumes seamlessly.
* **Defensive Rate-Limiting**: Implements request delays with randomized **jitter** (1.5s–3.5s) to minimize server load and mimic human request patterns.
* **Exponential Backoff**: Automatically retries transient network errors (`5xx`, timeouts) up to `MAX_RETRIES` before flagging as failed.
* **Compliant CAPTCHA Protocol**: Detects CAPTCHA challenges or login paywalls and cleanly pauses processing, prompting human verification rather than executing automated bypasses.
* **Complete Audit Snapshot**: Includes automated CSV export scripts for dataset snapshots and verification.

---

## 📂 Repository Structure

```text
├── docs/
│   └── INVESTIGATION.md       # Site architecture, endpoint findings, and paywall analysis
├── schema.sql                 # MySQL table creation and constraint definitions
├── generate_synthetic.py      # Seed generator for large-scale pipeline stress testing
├── mysql_worker.py            # Primary worker engine with queue locking and retry logic
├── export_csv.py              # Snapshot exporter from MySQL to CSV
├── requirements.txt           # Python dependency specifications
└── README.md                  # System documentation and execution guide
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
* **Python 3.9+**
* **MySQL Server** (Running locally or via container)

### 2. Install Dependencies
```bash
pip install pymysql pandas requests beautifulsoup4
```

### 3. Initialize Database Schema
Create the database and execute `schema.sql`:
```bash
mysql -u root -p < schema.sql
```

---

## 🚀 Execution Guide

### Step 1: Seed the Queue
Populate the MySQL database with task IDs:
```bash
python generate_synthetic.py
```

### Step 2: Run the Resumable Worker
Launch the worker processing engine:
```bash
python mysql_worker.py
```

### Step 3: Export Dataset Snapshot
Generate a CSV export of all extracted records:
```bash
python export_csv.py
```

---

## 📹 Resumability & Fault-Tolerance Demo Instructions

To verify that the pipeline is fully resumable during evaluation or video demonstration:

1. **Start the pipeline**: Run `python mysql_worker.py`. Observe items being processed and saved to MySQL.
2. **Simulate a crash**: Press **`Ctrl + C`** mid-run to interrupt the worker.
3. **Restart the pipeline**: Run `python mysql_worker.py` again.
4. **Verify idempotency**: Observe that the worker reads the state table, skips all previously completed items, and immediately resumes work at the exact record where it was interrupted.

---

## 📝 Investigation Findings Summary

During site analysis of the target portal (`coa.gov.in`), network inspection revealed that search queries execute via `POST` requests to `search_architectResult.php`. Detailed record views are restricted behind a server-side login wall and subscription requirement.

In compliance with assignment guidelines, this pipeline demonstrates full extraction capabilities, state persistence, rate control, and fault tolerance against accessible sample records and structured synthetic data matching the real target schema.

