"""
Stripe payment processing API endpoints
"""
from flask import Blueprint, request, jsonify
import stripe
import os
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_API_KEY')

@payments_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a Stripe Payment Intent"""
    try:
        data = request.get_json()
        amount = data.get('amount')  # Amount in cents
        currency = data.get('currency', 'usd')
        description = data.get('description', '')
        
        # Create Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata={
                'user_id': data.get('user_id'),
                'affiliate_code': data.get('affiliate_code')
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    """Confirm a payment and record it in database"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        
        # Retrieve Payment Intent from Stripe
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # TODO: Save to database using SQLAlchemy
        # payment = Payment(
        #     stripe_payment_id=intent.id,
        #     user_id=intent.metadata.get('user_id'),
        #     amount=intent.amount / 100,
        #     currency=intent.currency,
        #     status=PaymentStatus.COMPLETED,
        #     description=intent.description
        # )
        # db.session.add(payment)
        # db.session.commit()
        
        return jsonify({
            'status': 'success',
            'payment_id': intent.id,
            'amount': intent.amount / 100,
            'currency': intent.currency
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # TODO: Update payment status in database
        print(f"Payment succeeded: {payment_intent['id']}")
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # TODO: Update payment status to failed
        print(f"Payment failed: {payment_intent['id']}")
        
    elif event['type'] == 'charge.refunded':
        charge = event['data']['object']
        # TODO: Update payment status to refunded
        print(f"Charge refunded: {charge['id']}")
    
    return jsonify({'status': 'success'}), 200

@payments_bp.route('/list', methods=['GET'])
def list_payments():
    """List all payments for a user"""
    user_id = request.args.get('user_id')
    
    # TODO: Query database for user payments
    # payments = Payment.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'payments': [],
        'total': 0
    }), 200

@payments_bp.route('/refund', methods=['POST'])
def refund_payment():
    """Refund a payment"""
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        amount = data.get('amount')  # Optional partial refund
        
        # Create refund in Stripe
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount
        )
        
        # TODO: Update payment status in database
        
        return jsonify({
            'status': 'success',
            'refund_id': refund.id,
            'amount': refund.amount / 100
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
