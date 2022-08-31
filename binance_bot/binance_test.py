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
        f = open("output.txt", "a")
        close = float(payload['c'])

        print(close)
        
        global closes
        closes.pop(0)
        closes.append(close)

        print(closes)

        f.write(str(len(closes)) + '\n')
        for i in range(5):
            print(closes[i])
            f.write(str(closes[i]) + '\n')

        closes_series = pd.Series(closes)
        global ETH_owned
        if ETH_owned == False:
            print("Buying")
            status = buy_order(close)
            if status:
                f.write("Purchase was successful\n")
                print("Purchase was successful")
        else:
            print("Selling")
            status = sell_order(close)
            if status:
                f.write("Sale was successful\n")
                print("Sale was successful")
        
        f.close()

def buy_order(close):
    f = open("output.txt", "a")

    balance = float(client.get_asset_balance(asset='USDT')['free'])
    quantity = (balance / close) * .99 #adjust for commission so the order doesn't get rejected for insufficient funds
    rounded_quantity = round((math.floor(quantity*100)/100), 2) #adjust for precision requirements
    print("Rounded quantity: {}".format(rounded_quantity))

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
        f.close()
        return False

    print("Order submitted for the purchase of {} ETH for ${}".format(rounded_quantity, rounded_quantity*close))
    f.write("Order submitted for the purchase of {} ETH for ${}\n".format(rounded_quantity, rounded_quantity*close))
    
    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))
    global ETH_owned
    ETH_owned = True
    global previous_order_quantity
    previous_order_quantity = rounded_quantity
    f.close()
    return True

def sell_order(close):
    f = open("output.txt", "a")

    global previous_order_quantity
    if previous_order_quantity == -1:
        previous_order_quantity = round(math.floor(float(client.get_asset_balance(asset='ETH')['free'])*100)/100 , 2)

    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))

    try:
        order = client.order_market_sell(
            symbol='ETHUSDT',
            quantity=previous_order_quantity)
    except Exception as e:
        print(e)
        f.close()
        return False
    global previous_purchase_price
    if previous_purchase_price != -1:
        profit = (previous_order_quantity*close) - (previous_order_quantity*previous_purchase_price)
        print("Order submitted for the sale of {} ETH for ${} and a profit of ${}".format(previous_order_quantity, previous_order_quantity*close, profit))
        f.write("Order submitted for the sale of {} ETH for ${} and a profit of ${}\n".format(previous_order_quantity, previous_order_quantity*close, profit))
    else:
        print("Order submitted for the sale of {} ETH for ${}".format(previous_order_quantity, previous_order_quantity*close))
        f.write("Order submitted for the sale of {} ETH for ${}\n".format(previous_order_quantity, previous_order_quantity*close))
    print(client.get_asset_balance(asset='ETH'))
    print(client.get_asset_balance(asset='USDT'))
    
    global ETH_owned
    ETH_owned = False
    f.close()
    return True

    
# api_key = "api_key"
# secret_key = "secret_key"

api_key = "api_test_key"
secret_key = "secret_test_key"

# SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1d"
SOCKET = "wss://testnet.binance.vision/ws/ethusdt@kline_1s"

# url = 'https://api.binance.com/api/v3/klines'
url = 'https://testnet.binance.vision/api/v3/klines'


efficiency_ratio = 10
short_ema = 5
long_ema = 28
envelope_percent = 5.8
global ETH_owned
global previous_order_quantity
previous_order_quantity = -1
global previous_purchase_price
previous_purchase_price = -1



symbol = 'ETHUSDT'
interval = '1h'
start = str(int(dt.datetime(2022,6,1).timestamp()*1000))
end = str(int(dt.datetime.today().timestamp()*1000))


par = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end}
data = pd.DataFrame(json.loads(requests.get(url, params= par).text))

global closes
closes = data[4].astype(dtype='float64').tolist()
print(closes)


with open('config.json') as json_file:
    config = json.load(json_file)
client = Client(config[api_key], config[secret_key], tld='us', testnet=True)

pprint.pprint("Balance: {}".format(client.get_account()))
ETH_owned = (float(client.get_asset_balance(asset='ETH')['free']) > .01)
print(client.get_asset_balance(asset='ETH')) 
print(client.get_asset_balance(asset='USDT'))
print("ETH owned: {}".format(ETH_owned))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

