import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env
load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
username = parsed.username
password = parsed.password
host = parsed.hostname
db_name = parsed.path[1:]

try:
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=db_name
    )
    cursor = conn.cursor()

    print("Checking 'agent' table structure...")
    
    # Add role column
    try:
        cursor.execute("ALTER TABLE agent ADD COLUMN role VARCHAR(20) DEFAULT 'agent'")
        print("Added 'role' column.")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print("'role' column already exists.")
        else:
            print(f"Error adding 'role': {err}")

    conn.commit()
    print("Database schema updated successfully.")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
