import requests
def send_order_to_ninjatrader(action, qty, instrument="MES 09-25"):
    url = "http://localhost:5000/ninjatrader/order"
    payload = { "action": action, "quantity": qty, "instrument": instrument }
    try:
        response = requests.post(url, json=payload)
        print(f"[✅ Sent] {payload} → {response.json()}")
    except Exception as e:
        print(f"[❌ Error] Failed to reach NinjaTrader bridge: {e}")
