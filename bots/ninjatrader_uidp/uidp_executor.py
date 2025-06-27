from ninja_bridge import send_order_to_ninjatrader
def place_trade(action, size):
    print(f"[📦 EXECUTOR] Sending {action} order for {size}")
    send_order_to_ninjatrader(action, size)
