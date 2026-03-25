import mysql.connector
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env
load_dotenv()

# Parse DATABASE_URL
db_url = os.getenv('DATABASE_URL')
# mysql+mysqlconnector://root:123456@localhost/insurance_db
parsed = urlparse(db_url)
username = parsed.username
password = parsed.password
host = parsed.hostname
db_name = parsed.path[1:]

def migrate():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=db_name
        )
        cursor = conn.cursor()

        print("1. Creating agency table if it doesn't exist...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agency (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(150) NOT NULL,
            contact_details VARCHAR(255),
            address TEXT,
            status VARCHAR(20) DEFAULT 'active',
            agent_limit INT DEFAULT 5,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Check if we need to insert a default agency
        cursor.execute("SELECT id FROM agency WHERE id = 1")
        if not cursor.fetchone():
            print("Inserting Default Agency...")
            cursor.execute("INSERT INTO agency (id, name, status, agent_limit) VALUES (1, 'Default Agency', 'active', 50)")

        def column_exists(table, column):
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{column}'")
            return cursor.fetchone() is not None

        print("2. Extending agent table...")
        if not column_exists('agent', 'agency_id'):
            cursor.execute("ALTER TABLE agent ADD COLUMN agency_id INT")
            cursor.execute("ALTER TABLE agent ADD CONSTRAINT fk_agent_agency FOREIGN KEY (agency_id) REFERENCES agency(id)")
            cursor.execute("UPDATE agent SET agency_id = 1 WHERE agency_id IS NULL")

        print("3. Extending customer table...")
        if not column_exists('customer', 'agency_id'):
            cursor.execute("ALTER TABLE customer ADD COLUMN agency_id INT")
            cursor.execute("ALTER TABLE customer ADD CONSTRAINT fk_customer_agency FOREIGN KEY (agency_id) REFERENCES agency(id)")
            cursor.execute("UPDATE customer SET agency_id = 1 WHERE agency_id IS NULL")
            
        print("4. Extending audit_log table...")
        if not column_exists('audit_log', 'agency_id'):
            cursor.execute("ALTER TABLE audit_log ADD COLUMN agency_id INT")
            cursor.execute("ALTER TABLE audit_log ADD CONSTRAINT fk_audit_log_agency FOREIGN KEY (agency_id) REFERENCES agency(id)")
            cursor.execute("UPDATE audit_log SET agency_id = 1 WHERE agency_id IS NULL")

        print("5. Elevating test user to super_admin...")
        cursor.execute("UPDATE agent SET role = 'super_admin' WHERE email = 'test@demo.com'")

        conn.commit()
        print("Migration completed successfully!")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate()
