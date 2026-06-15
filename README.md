# Open Source Healthcare Systems
## Integrated Clinical, ERP, & Business Intelligence Platform

This monorepo integrates three primary open-source platforms to create a unified healthcare capacity, resource planning, and analytics platform:

1.  **Care EMR (Open Healthcare Network)**: Clinical triage, patient registration, and decentralized capacity tracking.
2.  **Odoo ERP**: Resource planning, financial logs, and active partner directories.
3.  **Metabase BI**: Real-time analytical dashboard connected to the production database registry.
4.  **Odoo Connector**: Custom Odoo modules acting as a synchronization gateway between Care EMR and Odoo.

---

## 1. System Components & Access Directory

Below is the directory of all integrated applications, default ports, database names, and administrator credentials.

| Application / Service | Service Port | Access URL | Default Database | Default Admin Username | Default Admin Password |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Care EMR Frontend** | `4000` | `http://localhost:4000/` | *N/A (React Client)* | `care-admin` | `Ohcn@123` |
| **Care EMR Backend API**| `9000` | `http://localhost:9000/` | `care` | `care-admin` | `Ohcn@123` |
| **Odoo ERP UI** | `8069` | `http://localhost:8069/` | `care_odoo` | `admin` | `admin` |
| **Metabase BI Analytics**| `3000` | `http://localhost:3000/` | `care` (direct connect) | *Pre-configured Session* | *Pre-configured Session*|
| **MinIO Object Console**| `9001` | `http://localhost:9001/` | *N/A* | `minioadmin` | `minioadmin` |
| **MinIO Object API (S3)**| `9100` | `http://localhost:9100/` | *N/A* | `minioadmin` | `minioadmin` |
| **PostgreSQL Database** | `5433` | `localhost:5433` | `postgres` | `postgres` | `postgres` |
| **Redis Cache & Broker**| `6380` | `localhost:6380` | *N/A* | *No password* | *No password* |

---

## 2. Prerequisites
Ensure the target system has the following software installed:
*   **Docker & Docker Desktop** (with Compose v2+)
*   **Node.js** (v18 or v20+)
*   **npm** (Node Package Manager)
*   **Git**

---

## 3. Step-by-Step Installation & Run Guide

Follow these instructions to run the entire system on a fresh machine:

### Step 1: Clone the Codebase
Open your command terminal (PowerShell, Bash, or Command Prompt) and execute:
```bash
git clone https://github.com/neonvarun/HealthcareSystems.git
cd HealthcareSystems
```

### Step 2: Configure Environment Variables
Care Backend relies on docker environment files. The repository contains pre-configured credentials under `care/docker/`. 
Verify that the following configurations exist:
*   `care/docker/.prebuilt.env` (contains database and MinIO credentials)
*   `care/docker/.local.env` (contains Care to Odoo API sync links and API host configurations)

### Step 3: Build and Start all Backend Services
Deploy PostgreSQL, Redis, MinIO, Odoo ERP, Metabase BI, Celery background workers, and Care Django Backend using Docker Compose:
```bash
cd care

# Option A: If you have Make installed
make build
make up

# Option B: If running Docker Compose directly
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up -d --build
```
*Wait approximately 60 seconds for all containers to report as "healthy" before proceeding.*

### Step 4: Run Migrations and Load Dummy Data
Apply the database schemas and load the pre-configured clinical and staff fixtures:
```bash
# Option A: If using Make
make reset-and-setup

# Option B: If running commands inside the container
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py load_fixtures
```

### Step 5: Setup and Start Care Frontend
Open a **new terminal window**, navigate to the React frontend directory, install npm packages, and run the development server:
```bash
cd HealthcareSystems/care_fe
npm install
npm run setup            # Generates dynamic plugin mappings (pluginMap.ts)
npm run local            # Runs Vite local server in docker mode
```
The React frontend is now compiled and listening at `http://localhost:4000/`.

---

## 4. Verifying the Integration

### 1. EMR to Odoo Real-Time Sync
1.  Open `http://localhost:4000/` in Chrome and log in as `care-admin` / `Ohcn@123`.
2.  Navigate to **Organizations > Health Department > Users**.
3.  Click **Add User** and fill out the details (First Name, Username, Email, Phone, Password).
4.  Under **Responsibility Assignments**, assign a Designation (e.g. `Admin`).
5.  Click **Create User**. The backend signals will catch this event and sync it to Odoo via the API connector.
6.  Open Odoo ERP at `http://localhost:8069/` (login to database `care_odoo` with `admin`/`admin`).
7.  Go to the **Contacts** module; the user will immediately appear in the partner ledger.

### 2. Analytical Auditing with Metabase
1.  Open Metabase at `http://localhost:3000/`.
2.  Navigate to **New > SQL query**.
3.  Choose **Care Database (Production)** as your source.
4.  Run the following query to audit synced user registries:
    ```sql
    SELECT id, name, email, phone FROM res_partner ORDER BY id DESC LIMIT 5;
    ```
5.  Click **Get Answer** to view the live database logs.
