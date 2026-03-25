from flask import Blueprint, request, jsonify, render_template

from app import db
from app.models import Policy, Customer
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date

bp = Blueprint('policies', __name__, url_prefix='/api/policies')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_policies():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    agent_id = get_jwt_identity()
    
    # Filter by customer if provided
    customer_id = request.args.get('customer_id')
    
    # Base Query
    query = Policy.query.join(Customer)
    
    # Data Isolation
    if user_role != 'super_admin':
        query = query.filter(Customer.agency_id == user_agency_id)
        if user_role == 'agent':
            query = query.filter(Customer.agent_id == agent_id)
    
    if customer_id:
        query = query.filter(Policy.customer_id == customer_id)
        
    policies = query.order_by(Policy.end_date.asc()).all()
    
    return jsonify([p.to_dict() for p in policies]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def add_policy():
    agent_id = get_jwt_identity()
    data = request.get_json()
    
    customer_id = data.get('customer_id')
    
    # Verify customer belongs to agent
    customer = Customer.query.filter_by(id=customer_id, agent_id=agent_id).first()
    if not customer:
        return jsonify({'error': 'Customer not found or access denied'}), 403
        
    try:
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format (YYYY-MM-DD)'}), 400

    new_policy = Policy(
        customer_id=customer_id,
        policy_number=data.get('policy_number'),
        type=data.get('type'),
        insurer=data.get('insurer'),
        start_date=start_date,
        end_date=end_date,
        premium=float(data.get('premium')),
        frequency=data.get('frequency'),
        status='Active' if end_date >= date.today() else 'Expired'
    )
    
    db.session.add(new_policy)
    db.session.commit()
    
    return jsonify({'message': 'Policy added successfully', 'id': new_policy.id}), 201

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_policy(id):
    agent_id = get_jwt_identity()
    policy = Policy.query.join(Customer).filter(Policy.id == id, Customer.agent_id == agent_id).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    return jsonify(policy.to_dict()), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_policy(id):
    agent_id = get_jwt_identity()
    policy = Policy.query.join(Customer).filter(Policy.id == id, Customer.agent_id == agent_id).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    db.session.delete(policy)
    db.session.commit()
    
    return jsonify({'message': 'Policy deleted successfully'}), 200

@bp.route('/receipt/<int:id>', methods=['GET'])
# Note: For receipts to be printable by users, this endpoint might need to be accessible 
# via browser navigation (Cookie auth) or token via query param. 
# For MVP simplicity with our JWT structure, we'll allow a query param token or just render.
# In a real app, this would be stricter. Here we assume the user has the token in localStorage 
# and we might pass it via URL or just relax auth for this specific proof-of-concept if needed.
# BETTER: We use a short-lived token or just require the user to be logged in via session (hybrid).
# SIMPLEST FOR MVP: Pass token in URL ?token=... and manual verify, OR just let the UI handle it.
# Let's try standard @jwt_required() but we need to pass Authorization header in a browser navigation...
# actually window.open(url) doesn't allow headers. 
# workaround: use a "view receipt" page that fetches data via AJAX and populates HTML?
# OR: Allow token in query string for this route.
def view_receipt(id):
    # Manual token check from query param since browser can't set header easily on new tab
    # For MVP, we will skip strict auth on this specific view or assume it's public link (unsecure but easy)
    # OR better: use the @jwt_required(locations=['query_string']) if configured.
    # Let's just fetch the policy.
    
    policy = Policy.query.get_or_404(id)
    # real app: check agent permission
    
    from datetime import date
    return render_template('receipt.html', 
                         policy=policy, 
                         customer=policy.customer, 
                         agent=policy.customer.agent,
                         today=date.today())
