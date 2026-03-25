from flask import Blueprint, jsonify, send_file
from app import db
from app.models import Customer, Policy
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import role_required
import json
import io
from datetime import datetime

bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@bp.route('/backup', methods=['GET'])
@role_required('admin')
def download_backup():
    agent_id = get_jwt_identity()
    
    # 1. Fetch all data for this agent
    customers = Customer.query.filter_by(agent_id=agent_id).all()
    
    # 2. Serialize data
    data = {'backup_date': datetime.now().isoformat(), 'customers': []}
    
    for c in customers:
        cust_data = {
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'mobile': c.mobile,
            'address': c.address,
            'created_at': c.created_at.isoformat(),
            'policies': []
        }
        
        # Get policies for this customer
        policies = Policy.query.filter_by(customer_id=c.id).all()
        for p in policies:
            pol_data = {
                'id': p.id,
                'policy_number': p.policy_number,
                'insurer': p.insurer,
                'type': p.type,
                'premium': p.premium,
                'start_date': p.start_date.isoformat(),
                'end_date': p.end_date.isoformat(),
                'frequency': p.frequency,
                'status': p.status,
                'doc_path': p.doc_path
            }
            cust_data['policies'].append(pol_data)
            
        data['customers'].append(cust_data)
        
    # 3. Create JSON file in memory
    json_str = json.dumps(data, indent=4)
    mem = io.BytesIO()
    mem.write(json_str.encode('utf-8'))
    mem.seek(0)
    
    filename = f"insurance_backup_{datetime.now().strftime('%Y-%m-%d')}.json"
    
    return send_file(
        mem,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )
