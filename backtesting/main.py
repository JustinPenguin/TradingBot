import argparse
import datetime
import collections
import inspect

import logging
import time
import os.path

from ibapi.client import EClient
from ibapi.wrapper import EWrapper 
from ibapi.contract import *
from ibapi.ticktype import *


# types
from ibapi.common import * # @UnusedWildImport
from ibapi.order_condition import * # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from ibapi.order import * # @UnusedWildImport
from ibapi.order_state import * # @UnusedWildImport
from ibapi.execution import Execution
from ibapi.execution import ExecutionFilter
from ibapi.commission_report import CommissionReport
from ibapi.tag_value import TagValue

from ibapi.account_summary_tags import *

import threading
import time

class App(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
              "Price:", floatMaxString(price), "CanAutoExecute:", attrib.canAutoExecute,
              "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)
        else:
            print("error with price data")
        
    def historicalData(self, reqId: TickerId, bar: BarData):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    # def nextValidId(self, orderID: int):
    #     super().nextValidId(orderID)
    #     print("Order {} sent".format(orderID))
    #     return orderID

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    # def orderStatus(self, orderId: OrderId, status: str, filled: Decimal,
    #                 remaining: Decimal, avgFillPrice: float, permId: int,
    #                 parentId: int, lastFillPrice: float, clientId: int,
    #                 whyHeld: str, mktCapPrice: float):
    #     super().orderStatus(orderId, status, filled, remaining,
    #                         avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
    #     print("OrderStatus. Id:", orderId, "Status:", status, "Filled:", decimalMaxString(filled),
    #           "Remaining:", decimalMaxString(remaining), "AvgFillPrice:", floatMaxString(avgFillPrice),
    #           "PermId:", intMaxString(permId), "ParentId:", intMaxString(parentId), "LastFillPrice:",
    #           floatMaxString(lastFillPrice), "ClientId:", intMaxString(clientId), "WhyHeld:",
    #           whyHeld, "MktCapPrice:", floatMaxString(mktCapPrice))

    # def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
    #               orderState: OrderState):
    #     super().openOrder(orderId, contract, order, orderState)
    #     print("OpenOrder. PermId:", intMaxString(order.permId), "ClientId:", intMaxString(order.clientId), " OrderId:", intMaxString(orderId), 
    #           "Account:", order.account, "Symbol:", contract.symbol, "SecType:", contract.secType,
    #           "Exchange:", contract.exchange, "Action:", order.action, "OrderType:", order.orderType,
    #           "TotalQty:", decimalMaxString(order.totalQuantity), "CashQty:", floatMaxString(order.cashQty), 
    #           "LmtPrice:", floatMaxString(order.lmtPrice), "AuxPrice:", floatMaxString(order.auxPrice), "Status:", orderState.status,
    #           "MinTradeQty:", intMaxString(order.minTradeQty), "MinCompeteSize:", intMaxString(order.minCompeteSize),
    #           "competeAgainstBestOffset:", "UpToMid" if order.competeAgainstBestOffset == COMPETE_AGAINST_BEST_OFFSET_UP_TO_MID else floatMaxString(order.competeAgainstBestOffset),
    #           "MidOffsetAtWhole:", floatMaxString(order.midOffsetAtWhole),"MidOffsetAtHalf:" ,floatMaxString(order.midOffsetAtHalf))

    #     order.contract = contract
    #     self.permId2ord[order.permId] = order

    # def execDetails(self, reqId: int, contract: Contract, execution: Execution):
    #     super().execDetails(reqId, contract, execution)
    #     print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:", contract.currency, execution)

def setup(app):
    while app.isConnected() == False:

        app.connect("127.0.0.1", 7497, clientId=0)
    print("successfully connected")
    # app.disconnect()
    # ! [connect]
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                    app.twsConnectionTime()))

    # # ! [clientrun]
    app.run()
    print("running")
    # ! [clientrun]


        
    
print("Attempting to connect to the API")
app = App()
# the app will connect to the socket with connect. To disconnect, you will have to kill the process
try:
    connection_thread = threading.Thread(target = setup, args = (app,))
    connection_thread.start()

except:
    print("Connection failure")
    raise

time.sleep(1)

ETH_contract = Contract()
ETH_contract.symbol = 'ETH'
ETH_contract.secType = 'CRYPTO'
ETH_contract.currency = 'USD'
ETH_contract.exchange = 'PAXOS'

# AAPL_contract = Contract()
# AAPL_contract.symbol = 'AAPL'
# AAPL_contract.secType = 'STK'
# AAPL_contract.currency = 'USD'
# AAPL_contract.exchange = 'SMART'

print(ETH_contract)

# requesting live market data
app.reqMktData(0, ETH_contract, '', False, False, [])

# for i in range(91):
#     print(TickTypeEnum.to_str(i), i)

time.sleep(1)

# TRADES
# MIDPOINT
# BID
# ASK
# BID_ASK
# HISTORICAL_VOLATILITY
# OPTION_IMPLIED_VOLATILITY
# SCHEDULE

# requesting historical data to store for later backtesting and calculating the sma
# app.reqHistoricalData(0, ETH_contract, '', '1 D', '5 mins', 'BID_ASK', 0, 2, False, [])

# time.sleep(1)

# def MarketOrder(action:str, quantity:Decimal):
    
#     #! [market]
#     order = Order()
#     order.action = action
#     order.orderType = "MKT"
#     order.totalQuantity = quantity
#     # order.cashQty = 700
#     order.tif = 'IOC'
#     #! [market]
#     return order

# def LimitOrder(action:str, quantity:Decimal, limitPrice:float):
    
#     # ! [limitorder]
#     order = Order()
#     order.action = action
#     order.orderType = "LMT"
#     order.totalQuantity = quantity
#     order.lmtPrice = limitPrice
#     order.tif = 'IOC'
#     # ! [limitorder]
#     return order

# ETH_order = MarketOrder("BUY", .5)
# AAPL_order = MarketOrder("BUY", 1)

# print("placing order")
# app.placeOrder(app.nextOrderId(), contract=ETH_contract, order=ETH_order)

# time.sleep(1)
# contract = Contract()
# contract.symbol = "AAPL"
# contract.secType = "STK"
# contract.exchange = "SMART"
# contract.currency = "USD"


# order = Order()
# order.goodTillDate = "20230923 15:13:20 EST"
# order.tif = "GTD"
# order.totalQuantity = 1
# order.orderType = "LMT"
# order.lmtPrice = 100
# order.action = "BUY"

# app.placeOrder(app.nextOrderId(), contract=ETH_contract, order=ETH_order)
# app.placeOrder(app.nextOrderId(), contract=AAPL_contract, order=AAPL_order)





# BTC_contract = Contract()
# BTC_contract.symbol = 'BRR'
# BTC_contract.secType = 'FUT'
# BTC_contract.exchange = 'CMECRYPTO'

print("the end")

app.disconnect()





