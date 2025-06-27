#!/bin/bash

# 🛠️ 1. Create Bot Files
mkdir -p bots/ninjatrader_uidp

cat << 'PYEOF' > bots/ninjatrader_uidp/ninjatrader_flask_bridge.py
from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/ninjatrader/order', methods=['POST'])
def execute_order():
    data = request.json
    instrument = data.get("instrument", "MES 09-25")
    action = data.get("action", "BUY")
    quantity = data.get("quantity", 1)
    print(f"[🧠 UIDP BRIDGE] Received order: {action} {quantity} of {instrument}")
    return jsonify({"status": "executed", "details": data}), 200
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
PYEOF

cat << 'PYEOF' > bots/ninjatrader_uidp/ninja_bridge.py
import requests
def send_order_to_ninjatrader(action, qty, instrument="MES 09-25"):
    url = "http://localhost:5000/ninjatrader/order"
    payload = { "action": action, "quantity": qty, "instrument": instrument }
    try:
        response = requests.post(url, json=payload)
        print(f"[✅ Sent] {payload} → {response.json()}")
    except Exception as e:
        print(f"[❌ Error] Failed to reach NinjaTrader bridge: {e}")
PYEOF

cat << 'PYEOF' > bots/ninjatrader_uidp/uidp_executor.py
from ninja_bridge import send_order_to_ninjatrader
def place_trade(action, size):
    print(f"[📦 EXECUTOR] Sending {action} order for {size}")
    send_order_to_ninjatrader(action, size)
PYEOF

cat << 'PYEOF' > bots/ninjatrader_uidp/chart_logic.py
def fetch_renko_chart():
    return { "signal": "BUY", "timestamp": "2025-06-26T21:00:00Z" }
PYEOF

cat << 'PYEOF' > bots/ninjatrader_uidp/dao_treasury_logger.py
import json
def log_trade(data):
    with open("dao_treasury_log.json", "a") as f:
        f.write(json.dumps(data) + "\\n")
PYEOF

cat << 'PYEOF' > bots/ninjatrader_uidp/renko_alpha_bot.py
from chart_logic import fetch_renko_chart
from uidp_executor import place_trade
from dao_treasury_logger import log_trade

def analyze_and_trade():
    chart_data = fetch_renko_chart()
    if chart_data["signal"] == "BUY":
        place_trade("BUY", 1)
    elif chart_data["signal"] == "SELL":
        place_trade("SELL", 1)
    log_trade(chart_data)

if __name__ == "__main__":
    analyze_and_trade()
PYEOF

# 🔄 2. Install Flask
pip3 install flask --user

# 🔁 3. Launch Bridge (manual step)
echo -e "\n🚀 Run this to launch the Flask bridge:\n"
echo "python3 bots/ninjatrader_uidp/ninjatrader_flask_bridge.py"

# ✅ 4. Test (optional)
echo -e "\n🌐 Once running, test with:\n"
echo "curl -X POST http://localhost:5000/ninjatrader/order -H \"Content-Type: application/json\" -d '{\"instrument\":\"MES 09-25\",\"action\":\"BUY\",\"quantity\":1}'"

