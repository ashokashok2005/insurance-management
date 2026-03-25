print("Starting...", flush=True)
import mysql.connector
print("Imported mysql.connector", flush=True)
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash

# Load .env
load_dotenv()
print("Loaded env", flush=True)

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
parsed = urlparse(db_url)
username = parsed.username
password = parsed.password
host = parsed.hostname
db_name = parsed.path[1:]

email = 'ashokarun301105@gmail.com'
new_pass = generate_password_hash('admin123')
print("Generated hash", flush=True)

try:
    print(f"Connecting to {host}...", flush=True)
    conn = mysql.connector.connect(
        host=host,
        user=username,
        password=password,
        database=db_name
    )
    print("Connected!", flush=True)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM agent WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user:
        print(f"Updating user {email}...")
        cursor.execute("UPDATE agent SET password_hash = %s, role = 'admin', is_active = 1 WHERE email = %s", (new_pass, email))
    else:
        print(f"Creating user {email}...")
        cursor.execute(
            "INSERT INTO agent (email, password_hash, name, role, is_active, created_at) VALUES (%s, %s, 'Admin User', 'admin', 1, NOW())",
            (email, new_pass)
        )

    conn.commit()
    print("SUCCESS: Credentials updated.")

except mysql.connector.Error as err:
    print(f"Database Error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
