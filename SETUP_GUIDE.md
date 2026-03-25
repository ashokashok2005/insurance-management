# Complete Setup Guide - Insurance Policy Management System

## Prerequisites Installation

### 1. Install Python (if not already installed)
1. Download Python 3.11+ from: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   ```

### 2. MySQL Database Setup
Your MySQL is already installed (version 9.6.0).

#### Create the Database
Open Command Prompt and run:
```bash
mysql -u root -p
```

Then in MySQL prompt:
```sql
CREATE DATABASE insurance_db;
SHOW DATABASES;
EXIT;
```

## Application Setup

### Step 1: Configure Database Connection
The `.env` file has been updated with your MySQL credentials (empty password for root).

**Current configuration:**
```
DATABASE_URL=mysql+mysqlconnector://root:@localhost/insurance_db
```

If your MySQL root user has a password, update it to:
```
DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/insurance_db
```

### Step 2: Install Python Dependencies

Open PowerShell or Command Prompt in the project directory:
```bash
cd c:\Users\ELCOT\Insurance
```

Then install packages:
```bash
python -m pip install flask flask-sqlalchemy flask-cors flask-jwt-extended mysql-connector-python python-dotenv werkzeug pandas openpyxl
```

**OR** use the requirements file:
```bash
python -m pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python run.py
```

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

## Troubleshooting

### Issue: "Python was not found"
**Solution**: 
1. Reinstall Python and check "Add to PATH"
2. Or use full path: `C:\Python311\python.exe run.py`

### Issue: "mysql command not recognized"
**Solution**: 
1. Find MySQL installation (usually `C:\Program Files\MySQL\MySQL Server 9.0\bin`)
2. Use full path: `"C:\Program Files\MySQL\MySQL Server 9.0\bin\mysql.exe" -u root -p`

### Issue: Database connection error
**Solution**:
1. Verify MySQL is running
2. Check `.env` file has correct password
3. Ensure `insurance_db` database exists

### Issue: "Module not found" errors
**Solution**: Reinstall dependencies:
```bash
python -m pip install --upgrade -r requirements.txt
```

## Quick Start Testing

1. **Sign Up**: Create an agent account
2. **Add Customer**: Go to Customers → Add new customer
3. **Add Policy**: Go to Policies → Add policy for that customer
4. **Check Dashboard**: View stats and upcoming renewals
5. **Upload Document**: Click Upload on any policy
6. **Export Report**: Click "Export Excel" on Policies page

## Manual Alternative (if Python issues persist)

If you continue having Python PATH issues, you can:

1. Find your Python installation folder (e.g., `C:\Users\ELCOT\AppData\Local\Programs\Python\Python311`)
2. Use the full path for all commands:
   ```bash
   C:\Users\ELCOT\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt
   C:\Users\ELCOT\AppData\Local\Programs\Python\Python311\python.exe run.py
   ```

## Next Steps After Setup

Once the server is running:
- Access at `http://localhost:5000`
- Create your first agent account
- Start adding customers and policies
- Test all features as outlined in `walkthrough.md`
