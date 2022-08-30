import websocket, json, pprint
import pandas as pd
import pandas_ta as ta
import requests
import datetime as dt

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

import math




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
        top, bottom = KAMA_Envelope(data=closes_series, ratio=efficiency_ratio, short=short_ema, long=long_ema, percent=envelope_percent)
        global order_active
        if order_active == False:
            if close > top:
                print("Buying")
                status = buy_order(close)
                if status:
                    print("Purchase was successful")
            if close < bottom:
                print("Selling")
                status = sell_order(close)
                if status:
                    print("Sale was successful")
        #     print("Buying")
        #     status = buy_order(close)
        #     if status:
        #         print("Purchase was successful")
        # else:
        #     print("Selling")
        #     status = sell_order(close)
        #     if status:
        #         print("Sale was successful")
        
        


def KAMA_Envelope(data, ratio, short, long, percent):
    kama = ta.kama(close=data,length=ratio, fast=short, slow=long)
    last_kama = kama[kama.size-1]

    top = last_kama*(1+(percent/100))
    bottom = last_kama+(1-(percent/100))

    return (top, bottom)

def buy_order(close):
    balance = float(client.get_asset_balance(asset='USDT')['free'])
    quantity = balance / close
    rounded_quantity = (math.floor(quantity*100)/100) - .01
    print(rounded_quantity)
    print(client.get_asset_balance(asset='ETH')) 
    print(client.get_asset_balance(asset='USDT'))
    global previous_purchase_price
    previous_purchase_price = close

    try:
        order = client.order_market_buy(
            symbol='ETHUSDT',
            quantity=rounded_quantity)
    except BinanceAPIException as e:
        print(e)
        return False

    print("Order submitted for the purchase of {} ETH for ${}".format(rounded_quantity, rounded_quantity*close))
    
    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))
    global order_active
    order_active = True
    global previous_order_quantity
    previous_order_quantity = rounded_quantity
    return True

def sell_order(close):
    global previous_order_quantity
    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))
    try:
        order = client.order_market_sell(
            symbol='ETHUSDT',
            quantity=previous_order_quantity)
    except Exception as e:
        print(e)
        return False
    global previous_purchase_price
    print("Order submitted for the sale of {} ETH for ${} and a profit of ${}".format(previous_order_quantity, previous_order_quantity*close, previous_order_quantity*previous_purchase_price))
    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))
    
    global order_active
    order_active = False
    return True

    
api_key = "api_key"
secret_key = "secret_key"

# api_key = "api_test_key"
# secret_key = "secret_test_key"

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1d"
# SOCKET = "wss://testnet.binance.vision/ws/ethusdt@kline_1m"

url = 'https://api.binance.com/api/v3/klines'
# url = 'https://testnet.binance.vision/api/v3/klines'


efficiency_ratio = 10
short_ema = 5
long_ema = 28
envelope_percent = 5.8
global order_active
order_active = False
global previous_order_quantity
global previous_purchase_price



symbol = 'ETHUSDT'
interval = '1d'
start = str(int(dt.datetime(2021,9,1).timestamp()*1000))
end = str(int(dt.datetime.today().timestamp()*1000))


par = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end}
data = pd.DataFrame(json.loads(requests.get(url, params= par).text))

closes = data[4].astype(dtype='float64').tolist()
print(closes)


with open('config.json') as json_file:
    config = json.load(json_file)
client = Client(config[api_key], config[secret_key], tld='us', testnet=False)

pprint.pprint("Balance: {}".format(client.get_account()))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

