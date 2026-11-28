# Setup Guide - Hospital Management System

## Windows SQE demo with isolated synthetic data

The supported project Python is 3.11. Work from the repository root in PowerShell. Flask serves the integrated frontend and the API on the same origin. The steps below keep the database off the development path and suppress SMTP in the local demo.

```powershell
py -3.11 -m venv .venv
$python = (Resolve-Path .\.venv\Scripts\python.exe).Path
& $python -m pip install -r backend/requirements.txt -r requirements-test.txt
$demo = Join-Path $env:TEMP ("medihub-demo-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $demo | Out-Null
$dbPath = Join-Path $demo "demo.db"
$env:MEDIHUB_DATABASE_URI = "sqlite:///" + $dbPath.Replace('\', '/')
Set-Location backend
& $python -c "from app import app, db; from pathlib import Path; c=app.app_context(); c.push(); print(Path(db.engine.url.database).resolve()); c.pop()"
& $python -X utf8 seed_db.py
if ($LASTEXITCODE) { throw "Demo seed failed" }
& $python -c "from app import app; app.config.update(MAIL_SUPPRESS_SEND=True); app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)"
```

Confirm the printed engine path equals `$dbPath` before seeding. The demo seeder requests new passwords without echo. Open `http://127.0.0.1:5001/` and use the synthetic usernames printed by the seeder. For a reset, stop the server with Ctrl+C, return to the repository root, and repeat the unique temporary directory, seed and start steps. A reset switches to a fresh database and leaves `backend/instance/medihub-database.db` untouched. No Redis is required for the selected local booking/cancellation checks with outbound mail suppressed.

From the repository root, use `& $python -m pytest tests/team/unit tests/team/api`. The team fixtures seed disposable databases automatically. For browser tests, install Chromium with `& $python -m playwright install chromium` and point `MEDIHUB_BROWSER_ASSETS` at the verified Vue and Bootstrap assets. [Pinned browser asset setup](../tests/team/evidence/phase3/environment.md)

```powershell
$env:MEDIHUB_BROWSER_ASSETS = Join-Path $env:TEMP 'medihub-phase1-browser-assets'
& $python -m pytest tests/team/e2e --browser chromium
```

See the [evidence index](../tests/team/evidence/final-reconstruction/README.md) for generator commands, output paths and audit tool provenance. The remainder of this guide retains historical platform notes.

This is a simple guide to get the project running on your machine.

## What You Need

- Python 3.8 or higher
- Redis Server (for background tasks)
- A web browser (Chrome, Firefox, etc.)

## Step 1: Backend Setup

First, go to the backend folder and install all the required packages:

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Create Database with Sample Data

Run this script to create the database and add some test data (admin, doctors, patients):

```bash
python seed_db.py
```

This will create:
- **1 Admin account** (username: admin, password: admin)
- **3 Doctors** with different specializations:
  - Ajay Kumar (Cardiology) - 14 years exp, ₹1200 fee
  - Rajesh Verma (Neurology) - 12 years exp, ₹1400 fee
  - Aditya Tripathi (Orthopedics) - 8 years exp, ₹1000 fee
- **3 Sample Patients**
- **7-day availability** for all doctors (morning & evening slots)

## Step 3: Start the Backend Server

Now start the Flask server:

```bash
python app.py
```

Your backend will be running at `http://localhost:5000`

## Step 4: Start Frontend

Open another terminal and go to the frontend folder:

```bash
cd frontend
python -m http.server 3000
```

Your website will open at `http://localhost:3000`

## Step 5: Redis Setup (For Email Notifications)

If you want email notifications to work, install and start Redis:

**Install Redis (Ubuntu/WSL):**
```bash
sudo apt update
sudo apt install redis-server
```

**Start Redis:**
```bash
sudo service redis-server start
```

## Step 6: Start Background Workers (Optional)

These are needed for sending emails and reminders:

**Terminal - Celery Worker with Beat:**
```bash
cd backend
celery -A celery_tasks.imports:celery_app worker --beat --loglevel=info
```

This single command runs both the worker (for processing tasks) and beat (for scheduling) together.

## Quick Summary

At minimum, you need 2 terminals:
1. **Backend:** `python app.py` (in backend folder)
2. **Frontend:** `python -m http.server 3000` (in frontend folder)

For full features (emails), you need:
3. Redis running in background
4. Celery worker
5. Celery beat

## Login Credentials

After running `seed_db.py`, you can login as:

**Admin:**
- Username: `admin`
- Password: `admin`
- Email: admin@medihub.in

**Doctors:**
- **Ajay Kumar** (Cardiology):
  - Username: `ajay`
  - Password: `ajay.kumar123`
  - Email: ajay.kumar@medihub.in

- **Rajesh Verma** (Neurology):
  - Username: `rajesh`
  - Password: `rajesh`
  - Email: rajesh.verma@medihub.in

**Patients:**
- **Arjun Patel**:
  - Username: `arjun`
  - Password: `arjun`
  - Email: arjun.patel@gmail.com

- **Vikram Singh**:
  - Username: `vikram`
  - Password: `vikram`
  - Email: vikram.singh@gmail.com
