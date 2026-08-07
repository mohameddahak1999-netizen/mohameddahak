from flask import Flask, request
import ccxt
import os

app = Flask(__name__)
@app.route("/")
def home():
  return "البوت شغال وجاهز لاستقبال الويب هوك بنجاح!"


exchange = ccxt.binance({
    'apiKey': os.environ.get('BINANCE_API_KEY'),
    'secret': os.environ.get('BINANCE_SECRET_KEY'),
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    symbol = data.get('symbol', 'ETH/USDT')
    side = data.get('side', 'buy')
    
    try:
        exchange.set_leverage(3, symbol)
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        amount = (50 * 3) / price
        
        order = exchange.create_order(symbol, 'market', side, amount)
        
        if side == 'buy':
            tp_price = price * 1.01
            sl_price = price * 0.90
            exchange.create_order(symbol, 'take_profit_market', 'sell', amount, None, {'stopPrice': tp_price})
            exchange.create_order(symbol, 'stop_market', 'sell', amount, None, {'stopPrice': sl_price})
        else:
            tp_price = price * 0.99
            sl_price = price * 1.10
            exchange.create_order(symbol, 'take_profit_market', 'buy', amount, None, {'stopPrice': tp_price})
            exchange.create_order(symbol, 'stop_market', 'buy', amount, None, {'stopPrice': sl_price})
            
        return "Order Executed Successfully", 200
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
