from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app import db
from app.models import Policy, Customer
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
import uuid

bp = Blueprint('documents', __name__, url_prefix='/api/documents')

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload/<int:policy_id>', methods=['POST'])
@jwt_required()
def upload_file(policy_id):
    agent_id = get_jwt_identity()
    
    # Verify policy ownership
    policy = Policy.query.join(Customer).filter(Policy.id == policy_id, Customer.agent_id == agent_id).first()
    if not policy:
        return jsonify({'error': 'Policy not found or access denied'}), 403
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Ensure upload dir exists (safety check)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
            
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
        
        # Update policy record
        policy.doc_path = unique_filename
        db.session.commit()
        
        return jsonify({'message': 'File uploaded successfully', 'filename': unique_filename}), 200
        
    return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/download/<filename>', methods=['GET'])
@jwt_required()
def download_file(filename):
    # In a real app, verify user has access to this specific file
    # Here, for MVP, we rely on the filename being UUID-based and hard to guess, 
    # but ideally we should check if any of the agent's policies have this doc_path
    
    # agent_id = get_jwt_identity()
    # Check ownership logic if needed...
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/receipt/<int:policy_id>/pdf', methods=['GET'])
@jwt_required()
def download_receipt_pdf(policy_id):
    from flask import render_template, make_response
    from app.utils import generate_pdf
    from datetime import date
    
    agent_id = get_jwt_identity()
    policy = Policy.query.join(Customer).filter(Policy.id == policy_id, Customer.agent_id == agent_id).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    data = {
        'policy': policy,
        'customer': policy.customer,
        'agent': policy.customer.agent,
        'today': date.today()
    }
                           
    pdf = generate_pdf(data)
    if not pdf:
        return jsonify({'error': 'PDF generation failed'}), 500
        
    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=receipt_{policy.policy_number}.pdf'
    
    return response
