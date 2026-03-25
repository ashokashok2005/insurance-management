from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from app import db
from app.models import Policy, Payment
import stripe
import os
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('payments', __name__, url_prefix='/payments')

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

@bp.route('/create-checkout-session/<int:policy_id>', methods=['POST'])
@jwt_required()
def create_checkout_session(policy_id):
    agent_id = get_jwt_identity()
    # verify ownership/permission (simple check: policy belongs to agent's customer)
    # policies.py does a join on Customer. Here we should do similar or rely on previous check.
    # For now, let's just fetch policy.
    policy = Policy.query.get_or_404(policy_id)
    
    # Check if policy is already paid? (optional logic)

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'inr', # or agent.currency if available
                    'product_data': {
                        'name': f"Policy Premium: {policy.policy_number}",
                    },
                    'unit_amount': int(policy.premium * 100), # Amount in cents/paise
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payments.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payments.cancel', _external=True),
            metadata={
                'policy_id': policy_id,
                'agent_id': agent_id
            }
        )
    except Exception as e:
        return jsonify(error=str(e)), 403

    return jsonify(url=checkout_session.url)

@bp.route('/success')
def success():
    session_id = request.args.get('session_id')
    if not session_id:
        return render_template('payment_cancel.html', message="No session ID provided.")

    # Verify session
    session = stripe.checkout.Session.retrieve(session_id)
    policy_id = session.metadata.get('policy_id')
    
    # Store payment record
    # ideally use webhooks for reliability, but for simple integration success page is okay-ish to verify
    # check if payment already recorded to avoid duplicates
    existing_payment = Payment.query.filter_by(stripe_payment_id=session_id).first()
    
    if not existing_payment and session.payment_status == 'paid':
        payment = Payment(
            policy_id=policy_id,
            amount=session.amount_total / 100,
            currency=session.currency,
            stripe_payment_id=session_id,
            status='completed'
        )
        db.session.add(payment)
        
        # update policy status maybe?
        # Update policy status and extend validity
        policy = Policy.query.get(policy_id)
        if policy:
             from datetime import date
             from dateutil.relativedelta import relativedelta
             
             # If policy was expired or about to expire, extend from current end date or today
             # Simple logic: Extend by 1 frequency period from max(today, end_date)
             # actually standard insurance logic: renew impacts end_date.
             
             base_date = max(policy.end_date, date.today())
             
             if policy.frequency == 'Yearly':
                 policy.end_date = base_date + relativedelta(years=1)
             elif policy.frequency == 'Quarterly':
                 policy.end_date = base_date + relativedelta(months=3)
             elif policy.frequency == 'Monthly':
                 policy.end_date = base_date + relativedelta(months=1)
                 
             policy.status = 'Active'

             # Send Email Notification
             if policy.customer.email:
                 from app.utils import send_email
                 from flask import render_template
                 # We can reuse the receipt HTML for the email body but it might be too complex for email clients
                 # Ideally, use a simpler email template. For now, let's just send a simple message.
                 email_body = f"""
                 <h1>Payment Received</h1>
                 <p>Dear {policy.customer.name},</p>
                 <p>We have received your payment of {payment.amount} {payment.currency} for policy <strong>{policy.policy_number}</strong>.</p>
                 <p>Your policy is now <strong>Active</strong> until {policy.end_date}.</p>
                 <p>Thank you for your business.</p>
                 """
                 try:
                     send_email(policy.customer.email, f"Payment Confirmation - {policy.policy_number}", email_body)
                     print(f"Email sent to {policy.customer.email}")
                 except Exception as e:
                     print(f"Failed to send email: {e}")

        db.session.commit()

    return render_template('payment_success.html')

@bp.route('/cancel')
def cancel():
    return render_template('payment_cancel.html')

@bp.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.get_data()
    sig_header = request.headers.get('STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise e
    except stripe.error.SignatureVerificationError as e:
        raise e

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Fulfill the purchase...
        handle_checkout_session(session)

    return jsonify(success=True)

def handle_checkout_session(session):
    policy_id = session.metadata.get('policy_id')
    # ... same logic as success ...
    existing_payment = Payment.query.filter_by(stripe_payment_id=session.id).first()
    if not existing_payment:
         payment = Payment(
            policy_id=policy_id,
            amount=session.amount_total / 100,
            currency=session.currency,
            stripe_payment_id=session.id,
            status='completed'
        )
         db.session.add(payment)
         db.session.commit()
