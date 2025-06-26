# Stripe Webhook Listener
# Purpose: Logs donations + generates UIDP logs for ValorDrive

from flask import Flask, request
import json, os
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    event = json.loads(payload)

    log_path = "donate/stripe_checkout/stripe_donations.log"
    with open(log_path, "a") as f:
        f.write(f"{datetime.utcnow()} - {json.dumps(event)}\n")

    print(f"Received Stripe Event: {event.get('type')}")
    return '', 200

if __name__ == '__main__':
    app.run(port=5001)
