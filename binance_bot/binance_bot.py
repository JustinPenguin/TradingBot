import websocket, json, pprint
import pandas as pd
import pandas_ta as ta
import requests
import datetime as dt

from binance.client import Client
from binance.enums import *




def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    json_message = json.loads(message)
    payload = json_message['k']
    # pprint.pprint(payload)

    if payload['x'] == True:
        close = float(payload['c'])

        print(close)
        
        closes.pop(0)
        closes.append(close)

        print(closes)

        closes_series = pd.Series(closes)
        top, bottom = KAMA_Envelope(closes_series, efficiency_ratio, short_ema, long_ema, envelope_percent)
        if order_active == False:
            if close > top:
                print("Buying")
                buy_order(close)
            if close < bottom:
                print("Selling")
                sell_order(close)
        
        


def KAMA_Envelope(data, ratio, short, long, percent):
    kama = ta.kama(close=data,length=ratio, fast=short, slow=long)
    print(kama)

    top = kama*(1+(percent/100))
    bottom = kama+(1-(percent/100))
    print(top, bottom)

    return (top, bottom)

def buy_order(close):
    balance= client.get_asset_balance(asset='USDT')
    quantity = float(balance['free'])/close
    previous_order_quantity = quantity
    order = Client.order_market_buy(
        symbol='ETHUSDT',
        quantity=quantity)
    print(order)
    order_active = True
    print("Buy Order succesfully placed")

def sell_order(close):
    order = Client.order_market_sell(
        symbol='ETHUSDT',
        quantity=previous_order_quantity)
    print(order)
    order_active = False
    print("Sell Order succesfully placed")


    



SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1s"

efficiency_ratio = 10
short_ema = 5
long_ema = 28
envelope_percent = 5.8
order_active = False
previous_order_quantity = 0

url = 'https://api.binance.com/api/v3/klines'
symbol = 'ETHUSDT'
interval = '1d'
start = str(int(dt.datetime(2021,9,1).timestamp()*1000))
end = str(int(dt.datetime.today().timestamp()*1000))

par = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end}
data = pd.DataFrame(json.loads(requests.get(url, params= par).text))

closes = data[4].astype(dtype='float64').tolist()
print(closes)
print(type(closes))


with open('config.json') as json_file:
    config = json.load(json_file)
client = Client(config["api_key"], config["secret_key"], tld='us')

pprint.pprint("Balance: {}".format(client.get_account()))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

