import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
db_url = os.getenv('DATABASE_URL')
from urllib.parse import urlparse
parsed = urlparse(db_url)

conn = mysql.connector.connect(
    host=parsed.hostname,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path[1:]
)
cursor = conn.cursor(dictionary=True)

print("Checking Agents...")
cursor.execute("SELECT id, name, email, role, agency_id, is_active FROM agent")
agents = cursor.fetchall()
for a in agents:
    print(a)

print("\nChecking Agencies...")
cursor.execute("SELECT * FROM agency")
agencies = cursor.fetchall()
for ag in agencies:
    print(ag)

cursor.close()
conn.close()
