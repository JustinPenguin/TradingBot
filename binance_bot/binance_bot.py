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
    print("???")
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
        kama = ta.kama(close=closes_series,length=efficiency_ratio, fast=short_ema, slow=long_ema)
        print(kama)
        
            
            


def KAMA_Envelope(ratio, short, long, percent, closes):
    if len(closes < long):
        print("not enough data")
        return


def buy_order():
    order = Client.order_market_sell(
        symbol='ETHUSDT',
        quantity=100)

def sell_order():
    order = Client.order_market_sell(
        symbol='ETHUSDT',
        quantity=100)


    



SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1s"

efficiency_ratio = 10
short_ema = 5
long_ema = 28
envelope_percent = 5.8

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

print("Balance: {}".format(client.get_account()))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

