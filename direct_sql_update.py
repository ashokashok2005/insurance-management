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
cursor = conn.cursor()

hash_val = "pbkdf2:sha256:1000000$Fy7D7ZYGqHNHxjt6$0d79c6eefe9a2964440d7cef773ac79161f8791ac679c58db1782bd5dab59265"
print(f"Updating password hash for test@demo.com...")
cursor.execute("UPDATE agent SET password_hash = %s WHERE email = %s", (hash_val, 'test@demo.com'))
conn.commit()

print(f"Rows affected: {cursor.rowcount}")

cursor.close()
conn.close()
