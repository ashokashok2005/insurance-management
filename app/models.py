from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class Agency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact_details = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active') # active, suspended
    agent_limit = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    agents = db.relationship('Agent', backref='agency', lazy=True)
    customers = db.relationship('Customer', backref='agency', lazy=True)
    logs = db.relationship('AuditLog', backref='agency', lazy=True)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=True) # made nullable temporarily for backward compat
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    default_reminder_days = db.Column(db.Integer, default=30)
    currency = db.Column(db.String(10), default='INR')
    otp = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(20), default='agent') # agent, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customers = db.relationship('Customer', backref='agent', lazy=True)
    logs = db.relationship('AuditLog', backref='agent', lazy=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    policies = db.relationship('Policy', backref='customer', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    policy_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Life, Health, Motor, Other
    insurer = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    premium = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(20), nullable=False) # Monthly, Quarterly, Yearly
    status = db.Column(db.String(20), default='Active') # Active, Expired
    doc_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name, # Access relationship
            'policy_number': self.policy_number,
            'type': self.type,
            'insurer': self.insurer,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'premium': self.premium,
            'frequency': self.frequency,
            'status': self.status,
            'doc_path': self.doc_path
        }

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.String(50), nullable=True) # ID of affected item
    ip_address = db.Column(db.String(50), nullable=True)
    details = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='inr')
    stripe_payment_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    policy = db.relationship('Policy', backref=db.backref('payments', lazy=True))
