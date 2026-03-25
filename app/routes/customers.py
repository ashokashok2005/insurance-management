from flask import Blueprint, request, jsonify
from app import db
from app.models import Customer
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    agent_id = get_jwt_identity()
    
    # Search functionality
    query_term = request.args.get('q')
    
    # Base Query
    query = Customer.query
    
    # Data Isolation
    if user_role != 'super_admin':
        query = query.filter(Customer.agency_id == user_agency_id)
        if user_role == 'agent':
            query = query.filter(Customer.agent_id == agent_id)
    
    if query_term:
        search = f"%{query_term}%"
        query = query.filter((Customer.name.like(search)) | (Customer.mobile.like(search)))
    
    customers = query.order_by(Customer.created_at.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'mobile': c.mobile,
        'email': c.email,
        'address': c.address
    } for c in customers]), 200

@bp.route('/', methods=['POST'])
@jwt_required()
def add_customer():
    agent_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('name') or not data.get('mobile'):
        return jsonify({'error': 'Name and Mobile are required'}), 400
        
    new_customer = Customer(
        agent_id=agent_id,
        name=data.get('name'),
        mobile=data.get('mobile'),
        email=data.get('email'),
        address=data.get('address')
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify({'message': 'Customer added successfully', 'id': new_customer.id}), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    agent_id = get_jwt_identity()
    customer = Customer.query.filter_by(id=id, agent_id=agent_id).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    data = request.get_json()
    customer.name = data.get('name', customer.name)
    customer.mobile = data.get('mobile', customer.mobile)
    customer.email = data.get('email', customer.email)
    customer.address = data.get('address', customer.address)
    
    db.session.commit()
    
    return jsonify({'message': 'Customer updated successfully'}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    agent_id = get_jwt_identity()
    customer = Customer.query.filter_by(id=id, agent_id=agent_id).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    db.session.delete(customer)
    db.session.commit()
    
    from app.utils import log_user_action
    log_user_action(agent_id, "DELETE_CUSTOMER", target_id=id, details=f"Deleted customer {customer.name}")
    
    return jsonify({'message': 'Customer deleted successfully'}), 200
