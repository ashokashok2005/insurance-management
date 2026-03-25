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

print("Checking Audit Logs data...")
cursor.execute("SELECT * FROM audit_log LIMIT 10")
logs = cursor.fetchall()
for l in logs:
    print(l)

print("\nChecking Agent data...")
cursor.execute("SELECT id, name FROM agent")
agents = cursor.fetchall()
for a in agents:
    print(a)

cursor.close()
conn.close()
走吧
