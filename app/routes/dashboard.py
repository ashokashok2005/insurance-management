from flask import Blueprint, jsonify, request
from app import db
from app.models import Policy, Customer
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, timedelta, datetime
from sqlalchemy import func, extract

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        user_role = claims.get('role')
        user_agency_id = claims.get('agency_id')
        agent_id = get_jwt_identity()
        
        # Base queries
        cust_query = Customer.query
        pol_query = Policy.query.join(Customer)
        
        # Data Isolation
        if user_role != 'super_admin':
            cust_query = cust_query.filter(Customer.agency_id == user_agency_id)
            pol_query = pol_query.filter(Customer.agency_id == user_agency_id)
            if user_role == 'agent':
                cust_query = cust_query.filter(Customer.agent_id == agent_id)
                pol_query = pol_query.filter(Customer.agent_id == agent_id)

        total_customers = cust_query.count()
        total_policies = pol_query.count()
        
        today = date.today()
        expired_policies = pol_query.filter(Policy.end_date < today).count()
        
        # Renewals due this month
        start_month = today.replace(day=1)
        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
            
        renewals_this_month = pol_query.filter(
            Policy.end_date >= start_month,
            Policy.end_date < next_month
        ).count()
        
        return jsonify({
            'total_customers': total_customers,
            'total_policies': total_policies,
            'expired_policies': expired_policies,
            'renewals_this_month': renewals_this_month
        }), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/renewals', methods=['GET'])
@jwt_required()
def get_upcoming_renewals():
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    user_role = claims.get('role')
    user_agency_id = claims.get('agency_id')
    agent_id = get_jwt_identity()

    days = request.args.get('days', 30, type=int)
    today = date.today()
    limit_date = today + timedelta(days=days)
    
    # Query base
    query = Policy.query.join(Customer)
    
    if user_role != 'super_admin':
        query = query.filter(Customer.agency_id == user_agency_id)
        if user_role == 'agent':
            query = query.filter(Customer.agent_id == agent_id)

    policies = query.filter(
        Policy.end_date >= today,
        Policy.end_date <= limit_date
    ).order_by(Policy.end_date.asc()).all()
    
    return jsonify([{
        'id': p.id,
        'customer_name': p.customer.name,
        'policy_number': p.policy_number,
        'insurer': p.insurer,
        'end_date': p.end_date.isoformat(),
        'days_left': (p.end_date - today).days
    } for p in policies]), 200

@bp.route('/chart-data', methods=['GET'])
@jwt_required()
def get_chart_data():
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        user_role = claims.get('role')
        user_agency_id = claims.get('agency_id')
        agent_id = get_jwt_identity()
        
        # Policy Types Distribution
        count_query = db.session.query(Policy.type, func.count(Policy.id)).join(Customer)
        
        # Premium sum query
        premium_query = db.session.query(func.sum(Policy.premium).label('total')).join(Customer)
        
        if user_role != 'super_admin':
            count_query = count_query.filter(Customer.agency_id == user_agency_id)
            premium_query = premium_query.filter(Customer.agency_id == user_agency_id, Policy.status == 'Active')
            if user_role == 'agent':
                count_query = count_query.filter(Customer.agent_id == agent_id)
                premium_query = premium_query.filter(Customer.agent_id == agent_id)
        else:
            # For super admin premium query
            premium_query = premium_query.filter(Policy.status == 'Active')
            
        policy_counts = count_query.group_by(Policy.type).all()
        policy_distribution = {type_: count for type_, count in policy_counts}
        
        total_premium = premium_query.scalar() or 0
            
        return jsonify({
            'policy_distribution': policy_distribution,
            'total_active_premium': total_premium
        }), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/send-reminder/<int:policy_id>', methods=['POST'])
@jwt_required()
def send_reminder(policy_id):
    agent_id = get_jwt_identity()
    
    policy = Policy.query.join(Customer).filter(Policy.id == policy_id, Customer.agent_id == agent_id).first()
    
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
        
    # Logic to send email would go here
    # For MVP, we simulate success
    
    return jsonify({
        'message': f"Reminder sent to {policy.customer.name} for Policy {policy.policy_number}"
    }), 200
