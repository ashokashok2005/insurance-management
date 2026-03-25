# Quick Start Instructions

## IMPORTANT: Install Python First

The WindowsApps Python alias is not a real Python installation. You need to install Python properly.

### Step 1: Install Python

1. Go to: https://www.python.org/downloads/
2. Download Python 3.11 or later
3. **CRITICAL**: During installation, CHECK the box "Add Python to PATH"
4. Complete the installation

### Step 2: Create MySQL Database

Open Command Prompt and run:
```bash
"C:\Program Files\MySQL\MySQL Server 9.0\bin\mysql.exe" -u root -p
```

Then in MySQL:
```sql
CREATE DATABASE insurance_db;
EXIT;
```

### Step 3: Run the Application

**Option A: Use the Batch Script (Easiest)**
1. Double-click `start.bat` in the Insurance folder
2. It will automatically install dependencies and start the server

**Option B: Manual Commands**
Open Command Prompt in `c:\Users\ELCOT\Insurance` and run:
```bash
python -m pip install -r requirements.txt
python run.py
```

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## Troubleshooting

### "Python was not found"
- You need to install Python from python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal after installation

### Database Connection Error
- Make sure MySQL is running
- Verify the database `insurance_db` exists
- Check the `.env` file has the correct MySQL password

### Port Already in Use
- Another application is using port 5000
- Stop that application or change the port in `run.py`

## What to Do After Setup

1. Create an agent account (sign up)
2. Add customers
3. Add policies for those customers
4. Check the dashboard for renewal alerts
5. Upload documents to policies
6. Export reports

See `SETUP_GUIDE.md` for detailed information.
