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
