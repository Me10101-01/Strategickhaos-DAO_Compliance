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
