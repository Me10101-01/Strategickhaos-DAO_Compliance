#!/usr/bin/env python3
"""
UIDP Webhook Integration Server
Receives webhooks from Stripe and PayPal, processes via UIDP
Part of Day 4: UIDP Deployment
"""

from flask import Flask, request, jsonify
import json
import os
import hmac
import hashlib
from datetime import datetime
import sys

# Import UIDP executor
sys.path.insert(0, os.path.dirname(__file__))
from uidp_executor_enhanced import UIDPExecutor

app = Flask(__name__)
executor = UIDPExecutor()

# Configuration (MUST be loaded from environment variables in production)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
PAYPAL_WEBHOOK_ID = os.environ.get('PAYPAL_WEBHOOK_ID')

# Security check - fail loudly if production secrets not set
if not STRIPE_WEBHOOK_SECRET or STRIPE_WEBHOOK_SECRET == 'whsec_test_secret':
    print("⚠️  WARNING: STRIPE_WEBHOOK_SECRET not set or using test value!")
    print("   For testing only. DO NOT use in production.")
    STRIPE_WEBHOOK_SECRET = 'whsec_test_secret'  # Allow for testing

if not PAYPAL_WEBHOOK_ID or PAYPAL_WEBHOOK_ID == 'test_webhook_id':
    print("⚠️  WARNING: PAYPAL_WEBHOOK_ID not set or using test value!")
    print("   For testing only. DO NOT use in production.")
    PAYPAL_WEBHOOK_ID = 'test_webhook_id'  # Allow for testing

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'UIDP Webhook Server',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe webhook handler
    Processes payment events and triggers UIDP allocation
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    # SECURITY: Verify webhook signature
    # In production, MUST use stripe.Webhook.construct_event() with real signature verification
    # Current implementation is for TESTING ONLY
    if STRIPE_WEBHOOK_SECRET == 'whsec_test_secret':
        # Test mode - no signature verification
        print("⚠️  TESTING MODE: Webhook signature verification disabled")
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON'}), 400
    else:
        # Production mode - verify signature (requires stripe library)
        # TODO: Implement proper signature verification
        # import stripe
        # try:
        #     event = stripe.Webhook.construct_event(
        #         payload, sig_header, STRIPE_WEBHOOK_SECRET
        #     )
        # except stripe.error.SignatureVerificationError:
        #     return jsonify({'error': 'Invalid signature'}), 403
        print("⚠️  WARNING: Production signature verification not yet implemented!")
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON'}), 400
    
    # Log webhook receipt
    log_webhook('stripe', event)
    
    # Process payment events
    event_type = event.get('type')
    
    if event_type == 'payment_intent.succeeded':
        # Extract payment details
        payment_intent = event.get('data', {}).get('object', {})
        amount_cents = payment_intent.get('amount', 0)
        amount_dollars = amount_cents / 100.0
        transaction_id = payment_intent.get('id')
        
        # Process through UIDP
        result = executor.process_revenue(
            revenue_amount=amount_dollars,
            payment_processor='stripe',
            transaction_id=transaction_id,
            metadata={
                'stripe_event_id': event.get('id'),
                'stripe_event_type': event_type,
                'currency': payment_intent.get('currency', 'usd'),
                'customer': payment_intent.get('customer'),
                'description': payment_intent.get('description')
            }
        )
        
        return jsonify({
            'received': True,
            'uidp_result': {
                'transaction_id': result['uidp_transaction_id'],
                'charity_allocation': result['allocation']['charity_allocation'],
                'verification_hash': result['verification_hash']
            }
        }), 200
    
    elif event_type == 'charge.succeeded':
        # Alternative event type for charges
        charge = event.get('data', {}).get('object', {})
        amount_cents = charge.get('amount', 0)
        amount_dollars = amount_cents / 100.0
        transaction_id = charge.get('id')
        
        result = executor.process_revenue(
            revenue_amount=amount_dollars,
            payment_processor='stripe',
            transaction_id=transaction_id,
            metadata={
                'stripe_event_id': event.get('id'),
                'stripe_event_type': event_type,
                'currency': charge.get('currency', 'usd')
            }
        )
        
        return jsonify({'received': True}), 200
    
    else:
        # Other event types - log but don't process
        print(f"[WEBHOOK] Received Stripe event type: {event_type} (not processed)")
        return jsonify({'received': True, 'processed': False}), 200

@app.route('/webhook/paypal', methods=['POST'])
def paypal_webhook():
    """
    PayPal webhook handler
    Processes payment events and triggers UIDP allocation
    """
    payload = request.data
    
    # Verify webhook signature (simplified for testing)
    # In production, verify PayPal signature
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Log webhook receipt
    log_webhook('paypal', event)
    
    # Process payment events
    event_type = event.get('event_type')
    
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        # Extract payment details
        resource = event.get('resource', {})
        amount = resource.get('amount', {})
        amount_dollars = float(amount.get('value', 0))
        transaction_id = resource.get('id')
        
        # Process through UIDP
        result = executor.process_revenue(
            revenue_amount=amount_dollars,
            payment_processor='paypal',
            transaction_id=transaction_id,
            metadata={
                'paypal_event_id': event.get('id'),
                'paypal_event_type': event_type,
                'currency': amount.get('currency_code', 'USD'),
                'payer_email': resource.get('payer', {}).get('email_address')
            }
        )
        
        return jsonify({
            'received': True,
            'uidp_result': {
                'transaction_id': result['uidp_transaction_id'],
                'charity_allocation': result['allocation']['charity_allocation']
            }
        }), 200
    
    else:
        # Other event types - log but don't process
        print(f"[WEBHOOK] Received PayPal event type: {event_type} (not processed)")
        return jsonify({'received': True, 'processed': False}), 200

@app.route('/webhook/crypto', methods=['POST'])
def crypto_webhook():
    """
    Cryptocurrency webhook handler
    Processes blockchain payment notifications
    """
    payload = request.data
    
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Log webhook receipt
    log_webhook('crypto', event)
    
    # Extract payment details (format depends on crypto payment processor)
    amount = event.get('amount', 0)
    transaction_hash = event.get('transaction_hash')
    currency = event.get('currency', 'unknown')
    
    # Process through UIDP
    result = executor.process_revenue(
        revenue_amount=amount,
        payment_processor='crypto',
        transaction_id=transaction_hash,
        metadata={
            'currency': currency,
            'blockchain': event.get('blockchain'),
            'confirmations': event.get('confirmations'),
            'from_address': event.get('from_address')
        }
    )
    
    return jsonify({
        'received': True,
        'uidp_result': {
            'transaction_id': result['uidp_transaction_id'],
            'charity_allocation': result['allocation']['charity_allocation']
        }
    }), 200

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """API endpoint to retrieve UIDP statistics"""
    stats = executor.get_statistics()
    return jsonify(stats), 200

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """API endpoint to retrieve recent transactions"""
    limit = request.args.get('limit', 10, type=int)
    transactions = executor.get_transaction_history(limit=limit)
    return jsonify({'transactions': transactions}), 200

@app.route('/api/process', methods=['POST'])
def manual_process():
    """
    Manual processing endpoint for testing or manual transactions
    Useful for donations not processed through webhooks
    """
    data = request.json
    
    if not data or 'amount' not in data:
        return jsonify({'error': 'Amount required'}), 400
    
    amount = float(data['amount'])
    processor = data.get('processor', 'manual')
    transaction_id = data.get('transaction_id', f'manual_{datetime.utcnow().timestamp()}')
    
    result = executor.process_revenue(
        revenue_amount=amount,
        payment_processor=processor,
        transaction_id=transaction_id,
        metadata=data.get('metadata', {})
    )
    
    return jsonify(result), 200

def log_webhook(processor, event):
    """Log webhook events for debugging and audit"""
    log_dir = 'webhook_logs'
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    log_file = f'{log_dir}/{processor}_webhook_{timestamp}.json'
    
    with open(log_file, 'w') as f:
        json.dump({
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'processor': processor,
            'event': event
        }, f, indent=2)
    
    print(f"[WEBHOOK] Logged {processor} webhook to {log_file}")

def verify_stripe_signature(payload, sig_header, secret):
    """Verify Stripe webhook signature"""
    # Parse signature header
    signatures = {}
    for item in sig_header.split(','):
        key, value = item.split('=')
        signatures[key] = value
    
    # Get timestamp and signature
    timestamp = signatures.get('t')
    signature = signatures.get('v1')
    
    # Compute expected signature
    signed_payload = f'{timestamp}.{payload.decode()}'
    expected_sig = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(signature, expected_sig)

if __name__ == '__main__':
    print("=" * 60)
    print("UIDP Webhook Integration Server")
    print("=" * 60)
    print("Listening for webhooks from:")
    print("  - Stripe: /webhook/stripe")
    print("  - PayPal: /webhook/paypal")
    print("  - Crypto: /webhook/crypto")
    print("  - Manual: /api/process")
    print("\nAPI Endpoints:")
    print("  - Statistics: /api/statistics")
    print("  - Transactions: /api/transactions")
    print("  - Health: /health")
    print("=" * 60)
    print("\nStarting server on http://localhost:5001")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
