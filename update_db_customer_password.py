"""
Migration script: Add password_hash column to Customer table.
Run this once: python update_db_customer_password.py
"""
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE customer ADD COLUMN password_hash VARCHAR(255) NULL"))
        db.session.commit()
        print("Added password_hash column to Customer table.")
    except Exception as e:
        if 'Duplicate column' in str(e) or 'already exists' in str(e).lower():
            print("Column password_hash already exists. No changes needed.")
        else:
            print(f"Error: {e}")
