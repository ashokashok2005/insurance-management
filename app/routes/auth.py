from flask import Blueprint, request, jsonify
from app import db, jwt
from app.models import Agent
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if Agent.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_agent = Agent(email=email, name=name, role='agent', agency_id=1)
    new_agent.set_password(password)
    
    db.session.add(new_agent)
    db.session.commit()

    return jsonify({'message': 'Agent registered successfully', 'agency_id': 1}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    agent = Agent.query.filter_by(email=email).first()

    if agent and agent.check_password(password):
        if not agent.is_active:
            return jsonify({'error': 'Account deactivated. Contact Admin.'}), 403

        # Include role and agency_id in additional claims
        claims = {
            'role': agent.role,
            'agency_id': agent.agency_id
        }
        access_token = create_access_token(identity=str(agent.id), additional_claims=claims) 
        
        # Log Logic
        from app.utils import log_user_action
        log_user_action(agent.id, "LOGIN", details="Successful login")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'agent': {
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'role': agent.role,
                'agency_id': agent.agency_id
            }
        }), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    agent = Agent.query.get(current_user_id)
    if not agent:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify({
        'id': agent.id,
        'name': agent.name,
        'email': agent.email
    }), 200

# OTP Password Reset Routes
import random
from datetime import datetime, timedelta
from flask_mail import Message
from app import mail

@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    agent = Agent.query.filter_by(email=email).first()
    if not agent:
        # Security: Don't reveal if email exists, but for MVP we might want success
        print(f"\n[FORGOT PASSWORD] Email not found in database: {email}", flush=True)
        return jsonify({'message': 'If the email exists, an OTP has been sent.'}), 200
        
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store in DB
    agent.otp = otp
    agent.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()
    
    # Send Email (Simulated for simplicity)
    # To use real email, you need to enable 2-Step Verification in Google first.
    from flask import current_app
    current_app.logger.warning("=" * 40)
    current_app.logger.warning(f"  OTP for {email}")
    current_app.logger.warning(f"  Your OTP is: {otp}")
    current_app.logger.warning(f"  Valid for 10 minutes")
    current_app.logger.warning("=" * 40)
    
    return jsonify({'message': f'Your OTP is: {otp} (valid for 10 minutes). Also check the terminal.'}), 200

    # try:
    #     msg = Message("Reset Password - InsurAgent",
    #                   sender="noreply@insuragent.com",
    #                   recipients=[email])
    #     msg.body = f"Your OTP for password reset is: {otp}\n\nIt expires in 10 minutes."
    #     mail.send(msg)
    #     return jsonify({'message': 'OTP sent to your email.'}), 200
    # except Exception as e:
    #     print(f"Email Error: {e}")
    #     return jsonify({'error': f"Email failed: {str(e)}"}), 500

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    new_password = data.get('new_password')
    
    agent = Agent.query.filter_by(email=email).first()
    if not agent:
        return jsonify({'error': 'Invalid request'}), 400
        
    # Verify OTP
    if not agent.otp or agent.otp != otp:
        return jsonify({'error': 'Invalid OTP'}), 400
        
    # Verify Expiry
    if datetime.utcnow() > agent.otp_expiry:
        return jsonify({'error': 'OTP Expired'}), 400
        
    # Reset Password
    agent.set_password(new_password)
    agent.otp = None
    agent.otp_expiry = None
    db.session.commit()
    
    return jsonify({'message': 'Password reset successful'}), 200
