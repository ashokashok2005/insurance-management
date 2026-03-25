from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import Customer, Policy
from app import db

bp = Blueprint('customer_auth', __name__, url_prefix='/api/customer')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_id = data.get('login_id') # Email or Mobile
    password = data.get('password')

    if not login_id or not password:
        return jsonify({'error': 'Missing login ID or password'}), 400

    # Try finding by email OR mobile
    customer = Customer.query.filter((Customer.email == login_id) | (Customer.mobile == login_id)).first()

    if customer and customer.check_password(password):
        # Create token with identity='customer_ID' and role claim
        # We prefix ID to distinguish from agents: 'cust_1'
        access_token = create_access_token(identity=f"cust_{customer.id}", additional_claims={'role': 'customer'})
        return jsonify({
            'access_token': access_token, 
            'customer_name': customer.name
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/policies', methods=['GET'])
@jwt_required()
def get_my_policies():
    identity = get_jwt_identity() # e.g., 'cust_1'
    
    if not identity.startswith('cust_'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cust_id = int(identity.split('_')[1])
        policies = Policy.query.filter_by(customer_id=cust_id).all()
        return jsonify([p.to_dict() for p in policies]), 200
    except:
        return jsonify({'error': 'Invalid token'}), 401
