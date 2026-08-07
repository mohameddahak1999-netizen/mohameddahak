from flask import Flask, request
import ccxt
import os

app = Flask(__name__)

exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

@app.route("/")
def home():
    return "البوت شغال وجاهز لاستقبال الويب هوك بنجاح!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("symbol", "ETH/USDT")
    side = data.get("side", "buy")

    try:
        exchange.set_leverage(3, symbol)
        balance = exchange.fetch_balance()
        usdt_free = balance["USDT"]["free"]

        margin_to_use = usdt_free * 0.90
        ticker = exchange.fetch_ticker(symbol)
        price = ticker["last"]
        amount = (margin_to_use * 3) / price

        exchange.create_order(symbol, "market", side, amount)

        if side == 'buy':
            tp_price = price * (1 + (0.02 / 3))
            sl_price = price * (1 - (0.20 / 3))
            exchange.create_order(symbol, "limit", "sell", amount, tp_price, {"reduceOnly": True})
            exchange.create_order(symbol, "stop_market", "sell", amount, sl_price, {"reduceOnly": True})
        else:
            tp_price = price * (1 - (0.02 / 3))
            sl_price = price * (1 + (0.20 / 3))
            exchange.create_order(symbol, "limit", "buy", amount, tp_price, {"reduceOnly": True})
            exchange.create_order(symbol, "stop_market", "buy", amount, sl_price, {"reduceOnly": True})

        return "Order Executed Successfully", 200
    except Exception as e:
        return str(e), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
