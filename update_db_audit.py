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

    print("Checking 'audit_log' table...")
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id INT NOT NULL,
            action VARCHAR(50) NOT NULL,
            target_id VARCHAR(50),
            ip_address VARCHAR(50),
            details VARCHAR(255),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agent(id)
        )
    """)
    print("Table 'audit_log' verified/created.")

    conn.commit()
    print("Database schema updated successfully.")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
