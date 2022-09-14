# trading algorithm will recognise 3 soldiers candlestick pattern as an indicator to sell

# using websocket, retrieve real time ticker data and convert to candlestick data- which we can use to analyse above pattern
# will use alpaca api to subscribe to specific tickers

import websocket
import json
import requests
import sys
import dateutil.parser
from datetime import datetime

minutes_processed = {}
minute_candlesticks = []
current_tick = None
previous_tick = None
in_position = False

SYMBOL = "AAPL"
TICKERS = "Q.AAPL"
# PLEASE REGISTER WITH ALPACA API AND GENERATE API_KEY AND SECRET_KEY
API_KEY = ""
SECRET_KEY = ""

BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
POSITIONS_URL = "{}/v2/positions/{}".format(BASE_URL, SYMBOL)

HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}


def place_order(profit_price, loss_price):
    data = {
        "symbol": SYMBOL,
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "take_profit": {
            "limit_price": profit_price
        },
        "stop_loss": {
            "stop_price": loss_price
        }
    }

    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)

    response = json.loads(r.content)

    print(response)


def on_open(ws):
    print("opened")
    auth_data = {
        "action": "auth",
        "params": API_KEY
    }

    ws.send(json.dumps(auth_data))

    # send subscribe JSON message to server

    channel_data = {
        "action": "subscribe",
        "params": TICKERS
    }

    ws.send(json.dumps(channel_data))


def on_message(ws, message):
    global current_tick, previous_tick, in_position

    previous_tick = current_tick
    # .loads() converts JSON msg -> py dict
    current_tick = json.loads(message)[0]

    print(current_tick)
    print("<<< Received Tick >>>")
    print(f"<<< {current_tick['t']} @ {current_tick['bp']} >>>")
    tick_datetime_object = datetime.utcfromtimestamp(current_tick['t']/1000)
    # can accept minute as lowest unit of time, timestamp includes seconds
    tick_dt = tick_datetime_object.strftime('%Y-%m-%d %H:%M')

    print(tick_datetime_object.minute)
    print(tick_dt)

    # need to record first tick received as well as tick with changes in high/low price
    if not tick_dt in minutes_processed:
        # add to dict, to create candlestick
        minutes_processed[tick_dt] = True
        print(minutes_processed)

        if len(minute_candlesticks) > 0:
            minute_candlesticks[-1]['close'] = previous_tick['bp']

        minute_candlesticks.append({
            "minute": tick_dt,
            "open": current_tick['bp'],
            "high": current_tick['bp'],
            "low": current_tick['bp']
        })

    if len(minute_candlesticks) > 0:
        current_candlestick = minute_candlesticks[-1]
        if current_tick['bp'] > current_candlestick['high']:
            current_candlestick['high'] = current_tick['bp']
        if current_tick['bp'] < current_candlestick['low']:
            current_candlestick['low'] = current_tick['bp']

    print("<<< Candlesticks >>>")
    for candlestick in minute_candlesticks:
        print(candlestick)

    if len(minute_candlesticks) > 3:
        print("<<< There are more than 3 candlesticks, checking for 3 soldiers pattern >>>")
        last_candle = minute_candlesticks[-2]
        previous_candle = minute_candlesticks[-3]
        first_candle = minute_candlesticks[-4]

        if last_candle['close'] > previous_candle['close'] and previous_candle['close'] > first_candle['close']:
            print("<<< Three green candlesticks in a row, TRADING! >>>")
            distance = last_candle['close'] - first_candle['open']
            print(f"<<< Distance: {distance} >>>")
            profit_price = last_candle['close'] + (distance * 2)
            print(f"<<< Profit: {profit_price} >>>")
            loss_price = first_candle['open']
            print(f"<<< Loss: {loss_price} >>>")

            if not in_position:
                print("<<< Placing order, position will be set to true >>>")
                in_position = True
                place_order(profit_price, loss_price)
                sys.exit()
        else:
            print("<<< NO GO! >>>")


def on_close(ws):
    print("<<< Connection closed >>>")


socket = "wss://alpaca.socket.polygon.io/stocks"

ws = websocket.WebSocketApp(socket, on_open=on_open,
                            on_message=on_message, on_close=on_close)
ws.run_forever()
