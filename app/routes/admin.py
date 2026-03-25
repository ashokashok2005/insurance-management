from flask import Blueprint, jsonify, request
from app import db
from app.models import Agent, AuditLog
from app.utils import role_required, log_user_action
from flask_jwt_extended import get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/users', methods=['GET'])
@role_required(['agency_admin', 'super_admin'])
def get_users():
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    
    query = Agent.query
    if user_role != 'super_admin':
        # Agency admins only see agents in their agency
        query = query.filter_by(agency_id=user_agency_id)
        
    agents = query.all()
    
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'email': a.email,
        'role': a.role,
        'is_active': a.is_active,
        'created_at': a.created_at.isoformat()
    } for a in agents]), 200

@bp.route('/users', methods=['POST'])
@role_required(['agency_admin', 'super_admin'])
def add_user():
    claims = get_jwt()
    user_agency_id = claims.get('agency_id')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'agent')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
        
    if Agent.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
        
    new_agent = Agent(
        email=email,
        name=name,
        role=role,
        agency_id=user_agency_id # Automatically bind to same agency
    )
    new_agent.set_password(password)
    
    db.session.add(new_agent)
    db.session.commit()
    
    log_user_action(get_jwt_identity(), "ADD_AGENT", target_id=new_agent.id, details=f"Added agent {email} to agency {user_agency_id}")
    
    return jsonify({'message': 'Agent added successfully', 'id': new_agent.id}), 201

@bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@role_required(['agency_admin', 'super_admin'])
def toggle_user_status(user_id):
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    current_agent_id = int(get_jwt_identity())
    
    if user_id == current_agent_id:
        return jsonify({'error': 'Cannot deactivate yourself'}), 400
        
    agent = Agent.query.get(user_id)
    if not agent:
        return jsonify({'error': 'User not found'}), 404
        
    # Permission check
    if user_role != 'super_admin' and agent.agency_id != user_agency_id:
        return jsonify({'error': 'Access denied: User belongs to another agency'}), 403
        
    agent.is_active = not agent.is_active
    db.session.commit()
    
    status = "activated" if agent.is_active else "deactivated"
    log_user_action(current_agent_id, "TOGGLE_USER_STATUS", target_id=user_id, details=f"User {agent.email} {status}")
    
    return jsonify({'message': f'User {status} successfully', 'is_active': agent.is_active}), 200

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@role_required(['agency_admin', 'super_admin'])
def admin_reset_password(user_id):
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    
    data = request.get_json()
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({'error': 'New password is required'}), 400
        
    agent = Agent.query.get(user_id)
    if not agent:
        return jsonify({'error': 'User not found'}), 404
        
    # Permission check
    if user_role != 'super_admin' and agent.agency_id != user_agency_id:
        return jsonify({'error': 'Access denied'}), 403
        
    agent.set_password(new_password)
    db.session.commit()
    
    log_user_action(get_jwt_identity(), "ADMIN_RESET_PASSWORD", target_id=user_id, details=f"Reset password for {agent.email}")
    
    return jsonify({'message': 'Password reset successful'}), 200

@bp.route('/audit-logs', methods=['GET'])
@role_required(['agency_admin', 'super_admin'])
def get_audit_logs():
    print("DEBUG: Fetching audit logs...")
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    
    query = AuditLog.query
    if user_role != 'super_admin':
        query = query.filter_by(agency_id=user_agency_id)
        
    logs = query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    return jsonify([{
        'id': l.id,
        'agent_name': l.agent.name if l.agent else 'System',
        'action': l.action,
        'target_id': l.target_id,
        'ip_address': l.ip_address,
        'details': l.details,
        'timestamp': l.timestamp.isoformat() if l.timestamp else None
    } for l in logs]), 200

@bp.route('/reassign', methods=['POST'])
@role_required(['agency_admin', 'super_admin'])
def reassign_records():
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    
    data = request.get_json()
    from_agent_id = data.get('from_agent_id')
    to_agent_id = data.get('to_agent_id')
    
    if not from_agent_id or not to_agent_id:
        return jsonify({'error': 'Source and Target agents are required'}), 400
        
    from_agent = Agent.query.get(from_agent_id)
    to_agent = Agent.query.get(to_agent_id)
    
    if not from_agent or not to_agent:
        return jsonify({'error': 'One or both agents not found'}), 404
        
    # Permission check: Agents must be in the same agency as the admin
    if user_role != 'super_admin':
        if from_agent.agency_id != user_agency_id or to_agent.agency_id != user_agency_id:
            return jsonify({'error': 'Access denied: Agents must belong to your agency'}), 403
            
    # Reassign all customers
    from app.models import Customer
    customers = Customer.query.filter_by(agent_id=from_agent_id).all()
    count = 0
    for c in customers:
        c.agent_id = to_agent_id
        count += 1
        
    db.session.commit()
    
    log_user_action(get_jwt_identity(), "REASSIGN_RECORDS", details=f"Reassigned {count} customers from {from_agent.email} to {to_agent.email}")
    
    return jsonify({'message': f'Successfully reassigned {count} customers and their policies'}), 200
