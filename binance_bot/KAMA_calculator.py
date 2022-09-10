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

from signal import signal, SIGPIPE, SIG_DFL 
#Ignore SIG_PIPE and don't throw exceptions on it... (http://docs.python.org/library/signal.html)
signal(SIGPIPE,SIG_DFL) 

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('parameters', [5.8,10,5,28]),
    )

    def __init__(self):
        self.kama = bt.indicators.KAMAEnvelope(period=self.params.parameters[1], fast=self.params.parameters[2], slow=self.params.parameters[3], perc=self.params.parameters[0])


    def stop(self):
        print(self.kama.top[0])
        print(self.kama.bot[0])
    


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    cerebro.addsizer(bt.sizers.PercentSizerInt)
    cerebro.addstrategy(TestStrategy)


    # df = pd.read_csv("live_data.csv", header = 0)

    # reverse data and save
    # df.to_csv('live_data.csv')

    data = btfeeds.GenericCSVData(
        dataname='live_data.csv',

        fromdate=datetime.datetime(2020, 9, 1),
        todate=datetime.datetime(2022, 9, 1),

        nullvalue=0.0,

        dtformat=('%Y-%m-%d'),

        datetime=0,

        open=1,
        high=2,
        low=3,
        close=4,
        volume=-1,
        openinterest=-1,
    )


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    cerebro.run(maxcpus=20)