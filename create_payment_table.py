from app import create_app, db
from app.models import Payment

app = create_app()

with app.app_context():
    # This will create any tables that don't exist, including Payment
    db.create_all()
    print("Database tables created successfully (if they didn't exist).")
