from flask import Blueprint, send_file
from app import db
from app.models import Policy, Customer
from flask_jwt_extended import jwt_required, get_jwt_identity
import pandas as pd
from io import BytesIO
from datetime import datetime

bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@bp.route('/export', methods=['GET'])
@jwt_required()
def export_policies():
    agent_id = get_jwt_identity()
    
    # Query all policies for the agent
    policies = Policy.query.join(Customer).filter(Customer.agent_id == agent_id).all()
    
    # Prepare data for DataFrame
    data = []
    for p in policies:
        data.append({
            'Policy Number': p.policy_number,
            'Customer Name': p.customer.name,
            'Insurer': p.insurer,
            'Type': p.type,
            'Start Date': p.start_date,
            'End Date': p.end_date,
            'Premium': p.premium,
            'Frequency': p.frequency,
            'Status': p.status
        })
        
    df = pd.DataFrame(data)
    
    # Create Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Policies')
        
    output.seek(0)
    
    filename = f"Policies_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
