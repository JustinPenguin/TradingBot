import websocket, json, pprint
import pandas as pd
import pandas_ta as ta
import requests
import datetime as dt


import numpy as np

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException

import math
from subprocess import run

import datetime
import csv

1662782400
1662800400

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    json_message = json.loads(message)
    payload = json_message['k']
    print(payload)

    global one_time_buy
    if payload['x'] == True or one_time_buy == True:
        f = open("output.txt", "a")

        t = payload['t']
        o = payload['o']
        h = payload['h']
        l = payload['l']
        c = payload['c']

        t = datetime.datetime.fromtimestamp((t / 1e3))
        data.loc[len(data.index)] = [t, o, h, l, c] 

        data.to_csv("live_data.csv", index = False)

        c = float(c)
        print(c)
        


        top, bottom = KAMA_Envelope()
        print("Top: {} Bottom: {} Close: {}" .format(top, bottom, c))
        f.write("Top: {} Bottom: {} Close: {}" .format(top, bottom, c))
        global ETH_owned
        if ETH_owned == False:
            if c > top:
                print("Buying")
                status = buy_order(c)
                if status:
                    f.write("Purchase was succesful\n")
                    print("Purchase was successful")
        else:
            if c < bottom:
                print("Selling")
                status = sell_order(c)
                if status:
                    f.write("Sale was successful\n")
                    print("Sale was successful")

        f.close()


def KAMA_Envelope():
    output = run(["python3", "KAMA_calculator.py"])
    f = open("kama.txt", "r")
    top = float(f.readline())
    bot = float(f.readline())
    f.close()
    
    return (top, bot)

def buy_order(close):
    f = open("output.txt", "a")

    balance = float(client.get_asset_balance(asset='USD')['free'])
    quantity = (balance / close) * .95 #adjust for commission so the order doesn't get rejected for insufficient funds
    rounded_quantity = round((math.floor(quantity*100)/100), 2) #adjust for precision requirements
    print("Rounded quantity: {}".format(rounded_quantity))

    print(client.get_asset_balance(asset='ETH')) 
    print(client.get_asset_balance(asset='USD'))

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
    print(client.get_asset_balance(asset='USD'))
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
    print(client.get_asset_balance(asset='USD'))

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
    print(client.get_asset_balance(asset='USD'))
    
    global ETH_owned
    ETH_owned = False
    f.close()
    return True


# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', 1000)
# pd.set_option('display.colheader_justify', 'center')
# pd.set_option('display.precision', 2)
    
api_key = "api_key"
secret_key = "secret_key"

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1d"

url = 'https://api.binance.com/api/v3/klines'


length = 10
fast_ema = 5
slow_ema = 28
envelope_percent = 5.8
global ETH_owned
global previous_order_quantity
previous_order_quantity = -1
global previous_purchase_price
previous_purchase_price = -1

global one_time_buy
one_time_buy = True



symbol = 'ETHUSDT'
interval = '1d'
start = str(int(dt.datetime(2021,8,1).timestamp()*1000))
end = str(int(dt.datetime.today().timestamp()*1000))

global data
par = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end}
data = pd.DataFrame(json.loads(requests.get(url, params= par).text))
data = data.iloc[:, :5]
print(data)


transformed_data = data
transformed_data[0] = pd.to_datetime(data[0], unit='ms')
transformed_data.to_csv("live_data.csv", index = False)
print(transformed_data)


with open('config.json') as json_file:
    config = json.load(json_file)
client = Client(config[api_key], config[secret_key], tld='us', testnet=False)

pprint.pprint("Balance: {}".format(client.get_account()))
ETH_owned = (float(client.get_asset_balance(asset='ETH')['free']) > .01)
print(client.get_asset_balance(asset='ETH')) 
print(client.get_asset_balance(asset='USD'))
print("ETH owned: {}".format(ETH_owned))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

