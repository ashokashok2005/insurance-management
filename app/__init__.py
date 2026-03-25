from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    
    db_url = os.getenv('DATABASE_URL')
    # If on Vercel and DB URL is localhost or missing, use SQLite in /tmp
    if os.getenv('VERCEL') == '1':
        if not db_url or 'localhost' in db_url or '127.0.0.1' in db_url:
            db_url = 'sqlite:////tmp/insurance_dev.db'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///insurance_dev.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    
    # Mail Config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    from app.routes import auth, customers, policies, dashboard, documents, reports, views, settings, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(policies.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(documents.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(views.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(admin.bp)

    from app.routes import payments
    app.register_blueprint(payments.bp)

    from app.routes import customer_auth
    app.register_blueprint(customer_auth.bp)

    from app.routes import superadmin
    app.register_blueprint(superadmin.bp)

    # Create DB tables if not exist (for MVP simplicity)
    # Wrap in try-except to prevent hard crash if DB is not reachable on Vercel startup
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database initialization error: {e}")
            # Do not re-throw here to allow the app to boot even if DB is down 
            # (it will 500 on DB routes, but at least the gateway can load the app)

    return app
