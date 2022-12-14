from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.analyzers as btanalyzers
import backtrader.feeds as btfeeds
import backtrader.strategies as btstrats

import yfinance as yf
import pandas as pd

import numpy as np

import sys
import errno
import random

from signal import signal, SIGPIPE, SIG_DFL 
#Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)
signal(SIGPIPE,SIG_DFL) 

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('parameters', [1.5,10,2,30]),
        ('printlog', False),
        ('progress', False),
        ('starting_price', 0),
        ('ending_price', 0),
        ('sizer_percent',99),
        ('portfolio_value', 0),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            tm = self.datas[0].datetime.time()
            print('%s, %s, %s' % (dt.isoformat(), tm, txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.first_price = True
        # Add a MovingAverageSimple indicator
        self.kama = bt.indicators.KAMAEnvelope(period=self.params.parameters[1], fast=self.params.parameters[2], slow=self.params.parameters[3], perc=self.params.parameters[0])


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:

            if order.isbuy():
                self.log('Sizer Percent: {}'.format(self.params.sizer_percent))
                self.log('Broker value: {}'.format(self.broker.getvalue()))
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size %.2f, Value %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size,
                     order.executed.value))
                

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buysize = order.executed.size
            else:  # Sell
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Size %.2f, Value %.2f' %
                        (order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                        order.executed.size,
                        order.executed.value))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.first_price:
            self.params.starting_price = self.dataclose[0]
            self.first_price = False

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        buy_size = (self.broker.getvalue() * (self.params.sizer_percent/100))/self.dataclose[0]
        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.kama.top[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.log('Buy size: {}'.format(buy_size))
                self.order = self.buy(size=buy_size)

        else:

            if self.dataclose[0] < self.kama.bot[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.log('Sell size: {}'.format(self.buysize))
                self.order = self.sell(size=self.buysize)

    def stop(self):
        # self.log('(Percent %.2f) (Period %.2f) (Fast %.2f) (Slow %.2f) Ending Value %.2f' %
        #          (self.params.parameters[0], self.params.parameters[1], self.params.parameters[2], self.params.parameters[3], self.broker.getvalue()), doprint=self.params.progress)

        self.params.ending_price = self.dataclose[0]
        self.params.portfolio_value = self.broker.getvalue()
    


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats = False, exactbars=True, runonce = False)

    # Add a strategy
    period1 = range(5*24,20*24)
    period2 = range(1*24,20*24)
    period3 = range(1*24,40*24)
    percents = np.linspace(1,20,100)
    parameters = []
    for p in percents:
        if random.randint(1,10) % 10 == 0:
            
            for i in period1:
                if random.randint(1,10) % 10 == 0:
                    for j in period2:
                        if random.randint(1,10) % 10 == 0:
                                for k in period3:
                                    if k > j:
                                        if random.randint(1,5) % 5 == 0:
                                            parameters.append([p, i, j, k])

            
    log = sys.argv[1]
    progress = sys.argv[2]
    if log == "True":
        log = True
    else:
        log = False

    if progress == "True":
        progress == True
    else:
        progress == False

    print(log, progress)

    strats = cerebro.optstrategy(
    TestStrategy,
    parameters=parameters,
    printlog = log,
    progress = progress
    )
    cerebro.addsizer(bt.sizers.PercentSizerInt)
    # cerebro.addstrategy(TestStrategy)


    # data = bt.feeds.PandasData(dataname=yf.download('ETH-USD', '2020-09-20', '2022-07-25'))
    df = pd.read_csv("historical_data/Gemini_ETHUSD_1h.csv", header = 0)

    # reverse data and save
    df=df.iloc[::-1]
    df.set_index('date', inplace=True)
    df.to_csv('reversed.csv')

    data = btfeeds.GenericCSVData(
        dataname='reversed.csv',

        fromdate=datetime.datetime(2019, 5, 1),
        todate=datetime.datetime(2021, 7, 25),
        timeframe=bt.TimeFrame.Minutes,
        compression=60,

        nullvalue=0.0,

        dtformat=('%Y-%m-%d %H:%M:%S'),

        datetime=0,

        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
    )


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cash = 100000
    cerebro.broker.setcash(cash)

    # Add a FixedSize sizer according to the stake

    # Set the commission
    cerebro.broker.setcommission(commission=0.0018)
    
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe', timeframe=bt.TimeFrame.Months)

    cerebro.addanalyzer(btanalyzers.VWR, _name='myVWR', tau=6, sdev_max=1, timeframe=bt.TimeFrame.Months)
    # Run over everything

    # for i in range(1,100):
    


    results = cerebro.run(maxcpus=20)
    # cerebro.plot()

    strats = [x[0] for x in results]
    def sharperatio(num):
        if num.analyzers.mysharpe.get_analysis()['sharperatio'] == None or num.params.portfolio_value < cash:
            num.analyzers.mysharpe.get_analysis()['sharperatio'] = 0
        return num.analyzers.mysharpe.get_analysis()['sharperatio']

    def VWR(num):
        if num.analyzers.myVWR.get_analysis()['vwr'] == None or num.params.portfolio_value < cash:
            num.analyzers.myVWR.get_analysis()['vwr'] = 0
        return num.analyzers.myVWR.get_analysis()['vwr']
    
    for i in reversed(range(-50,0)):
       
        strats.sort(key = sharperatio)
        print(strats[i].params.portfolio_value)
        print("Sizer percent: {}".format(strats[i].params.sizer_percent))
        print("Highest sharpe Ratio: {} Strategy: {} {} {} {}".format(strats[i].analyzers.mysharpe.get_analysis()['sharperatio'], strats[i].params.parameters[0], strats[i].params.parameters[1], strats[i].params.parameters[2], strats[i].params.parameters[3]))
        print("Its VWR: {}".format(strats[i].analyzers.myVWR.get_analysis()['vwr']))

        starting_price = strats[i].params.starting_price
        ending_price = strats[i].params.ending_price
        print(starting_price, " ", ending_price)
    
        buying_and_holding = (1 + ((ending_price - starting_price)/starting_price)) * cash
        print("Portoflio value from buying and holding: {}".format(buying_and_holding))

    for i in reversed(range(-50,0)):
        strats.sort(key = VWR)

        print(strats[i].params.portfolio_value)
        print("Sizer percent: {}".format(strats[i].params.sizer_percent))
        print("Highest VWR: {} Strategy: {} {} {} {}".format(strats[i].analyzers.myVWR.get_analysis()['vwr'], strats[i].params.parameters[0], strats[i].params.parameters[1], strats[i].params.parameters[2], strats[i].params.parameters[3]))
        print("Its sharpe ratio: {}".format(strats[i].analyzers.mysharpe.get_analysis()['sharperatio']))

        starting_price = strats[i].params.starting_price
        ending_price = strats[i].params.ending_price
        print(starting_price, " ", ending_price)
    
        buying_and_holding = (1 + ((ending_price - starting_price)/starting_price)) * cash
        print("Portoflio value from buying and holding: {}".format(buying_and_holding))
