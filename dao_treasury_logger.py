# 🧾 DAO Treasury Logger
import json
def log_trade(data):
    with open("dao_treasury_log.json", "a") as f:
        f.write(json.dumps(data) + "\\n")
