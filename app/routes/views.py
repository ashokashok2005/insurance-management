from flask import Blueprint, render_template

bp = Blueprint('views', __name__)

@bp.route('/')
def index():
    return render_template('base.html') # Logic in base.html handles redirection

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route('/register')
def register():
    return render_template('register.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/customers')
def customers():
    return render_template('customers.html')

@bp.route('/policies')
def policies():
    return render_template('policies.html')

@bp.route('/settings')
def settings():
    return render_template('settings.html')


@bp.route('/admin/users')
def admin_users_page():
    return render_template('admin_users.html')

@bp.route('/admin/audit-logs')
def audit_logs_page():
    return render_template('admin_audit.html')

@bp.route('/agencies')
def agencies_page():
    return render_template('agencies.html')

@bp.route('/customer/login')
def customer_login():
    return render_template('customer_login.html')

@bp.route('/customer/dashboard')
def customer_dashboard():
    return render_template('customer_dashboard.html')
