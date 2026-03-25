import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env
load_dotenv()

# Parse DATABASE_URL
# Format: mysql+mysqlconnector://user:password@host/db_name
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
username = parsed.username
password = parsed.password
host = parsed.hostname
db_name = parsed.path[1:] # remove leading /

try:
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=db_name
    )
    cursor = conn.cursor()

    print("Checking 'agent' table structure...")
    
    # Add otp column
    try:
        cursor.execute("ALTER TABLE agent ADD COLUMN otp VARCHAR(6) NULL")
        print("Added 'otp' column.")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("'otp' column already exists.")
        else:
            print(f"Error adding 'otp': {err}")

    # Add otp_expiry column
    try:
        cursor.execute("ALTER TABLE agent ADD COLUMN otp_expiry DATETIME NULL")
        print("Added 'otp_expiry' column.")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("'otp_expiry' column already exists.")
        else:
            print(f"Error adding 'otp_expiry': {err}")

    conn.commit()
    print("Database schema updated successfully.")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
