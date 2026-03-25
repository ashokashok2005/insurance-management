from flask import Blueprint, request, jsonify
from app import db
from app.models import Agency, Agent
from app.utils import role_required, log_user_action
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('superadmin', __name__, url_prefix='/api/superadmin')

@bp.route('/agencies', methods=['GET'])
@jwt_required()
@role_required('super_admin')
def get_agencies():
    agencies = Agency.query.all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'contact_details': a.contact_details,
        'address': a.address,
        'status': a.status,
        'agent_limit': a.agent_limit,
        'created_at': a.created_at.isoformat()
    } for a in agencies]), 200

@bp.route('/agencies', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def create_agency():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Agency name is required'}), 400
        
    new_agency = Agency(
        name=data.get('name'),
        contact_details=data.get('contact_details'),
        address=data.get('address'),
        agent_limit=data.get('agent_limit', 5)
    )
    db.session.add(new_agency)
    db.session.commit()
    
    log_user_action(get_jwt_identity(), "CREATE_AGENCY", target_id=new_agency.id, details=f"Created agency {new_agency.name}")
    
    return jsonify({'message': 'Agency created successfully', 'id': new_agency.id}), 201

@bp.route('/agencies/<int:id>/status', methods=['PUT'])
@jwt_required()
@role_required('super_admin')
def update_agency_status(id):
    agency = Agency.query.get_or_404(id)
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['active', 'suspended']:
        return jsonify({'error': 'Invalid status'}), 400
        
    agency.status = status
    db.session.commit()
    
    # Also deactivate/activate agents in that agency? 
    # For now, we just update the agency status. 
    # Login check for agent can verify agency status too.
    
    log_user_action(get_jwt_identity(), "UPDATE_AGENCY_STATUS", target_id=id, details=f"Updated agency {agency.name} status to {status}")
    
    return jsonify({'message': f'Agency status updated to {status}'}), 200

@bp.route('/assign-admin', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def assign_agency_admin():
    data = request.get_json()
    email = data.get('email')
    agency_id = data.get('agency_id')
    
    if not email or not agency_id:
        return jsonify({'error': 'Email and Agency ID are required'}), 400
        
    agent = Agent.query.filter_by(email=email).first()
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
        
    agent.agency_id = agency_id
    agent.role = 'agency_admin'
    db.session.commit()
    
    log_user_action(get_jwt_identity(), "ASSIGN_AGENCY_ADMIN", target_id=agent.id, details=f"Assigned {agent.email} as admin for agency {agency_id}")
    
    return jsonify({'message': 'Agency admin assigned successfully'}), 200
