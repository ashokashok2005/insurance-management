from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(required_roles):
    if isinstance(required_roles, str):
        required_roles = [required_roles]
        
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Simple Role Hierarchy
            # super_admin can do everything
            # agency_admin can do everything except super_admin tasks
            hierarchy = {
                'super_admin': ['super_admin', 'agency_admin', 'agent', 'admin'], # backward compat with 'admin'
                'agency_admin': ['agency_admin', 'agent', 'admin'],
                'agent': ['agent']
            }
            
            allowed = False
            for req in required_roles:
                if user_role == req or req in hierarchy.get(user_role, []):
                    allowed = True
                    break
                    
            if not allowed:
                return jsonify({'error': 'Access forbidden: Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

from flask import request
import datetime

def log_user_action(agent_id, action, target_id=None, details=None):
    # Import inside function to avoid circular import (app -> routes -> utils -> models -> app)
    from app import db
    from app.models import AuditLog
    from flask_jwt_extended import get_jwt
    
    try:
        # Try to get agency_id from JWT if available
        claims = {}
        try:
            verify_jwt_in_request(optional=True)
            claims = get_jwt()
        except:
            pass
            
        agency_id = claims.get('agency_id')
        ip = request.remote_addr
        log = AuditLog(
            agency_id=agency_id,
            agent_id=agent_id,
            action=action,
            target_id=str(target_id) if target_id else None,
            details=details,
            ip_address=ip,
            timestamp=datetime.datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Audit Log Error: {e}")

import io
from fpdf import FPDF
from flask_mail import Message
from flask import current_app

def generate_pdf(data):
    """
    Generate PDF using fpdf2 from structured data.
    Expected data: {
        'policy': policy_obj,
        'customer': customer_obj,
        'agent': agent_obj,
        'today': date_obj
    }
    """
    policy = data.get('policy')
    customer = data.get('customer')
    agent = data.get('agent')
    today = data.get('today')

    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(78, 84, 200) # #4e54c8
    pdf.cell(0, 20, "Insurance Manager", ln=True)
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(85, 85, 85)
    pdf.cell(0, 10, "PREMIUM RECEIPT", ln=True, align='R')
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # Billing Info
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(119, 119, 119)
    y_start = pdf.get_y()
    pdf.cell(95, 5, "BILLED TO:", ln=False)
    pdf.cell(95, 5, "RECEIPT DETAILS:", ln=True)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(51, 51, 51)
    
    # Column 1: Customer
    pdf.set_y(y_start + 5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(95, 6, customer.name, ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(90, 5, f"{customer.address}\n{customer.mobile}\n{customer.email or ''}")
    
    # Column 2: Details
    pdf.set_xy(105, y_start + 5)
    pdf.multi_cell(95, 6, f"Receipt #: REC-{policy.id}-{today}\nDate: {today}\nAgent: {agent.name}")
    
    pdf.ln(15)
    
    # Items Table Header
    pdf.set_fill_color(249, 249, 249)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(119, 119, 119)
    pdf.cell(80, 10, "Description", border=1, fill=True)
    pdf.cell(30, 10, "Type", border=1, fill=True)
    pdf.cell(40, 10, "Period", border=1, fill=True)
    pdf.cell(40, 10, "Amount", border=1, fill=True, align='R')
    pdf.ln()
    
    # Items Table Row
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(80, 15, f"{policy.insurer} - {policy.policy_number}", border=1)
    pdf.cell(30, 15, policy.type, border=1)
    pdf.cell(40, 15, policy.frequency, border=1)
    pdf.cell(40, 15, f"{policy.premium:.2f}", border=1, align='R')
    pdf.ln()
    
    # Total
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(150, 15, "Total Paid:", align='R')
    pdf.cell(40, 15, f"{policy.premium:.2f}", align='R')
    
    # Footer
    pdf.set_y(-30)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(119, 119, 119)
    pdf.cell(0, 10, "Thank you for your business! This is a computer-generated receipt.", align='C')
    
    # Return as bytes
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

def send_email(to, subject, html_content):
    """
    Send email using Flask-Mail
    """
    from app import mail
    try:
        msg = Message(subject,
                      sender=current_app.config.get('MAIL_USERNAME'),
                      recipients=[to])
        msg.html = html_content
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False
