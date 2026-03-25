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

def promote_to_admin():
    email = input("Enter the email of the user to make Admin: ")
    
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id, name, role FROM agent WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"Error: No user found with email '{email}'")
            return
            
        print(f"Found User: {user[1]} (Current Role: {user[2]})")
        
        # Update Role
        cursor.execute("UPDATE agent SET role = 'admin' WHERE email = %s", (email,))
        conn.commit()
        
        print(f"SUCCESS: User '{email}' is now an Admin!")
        
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    promote_to_admin()
