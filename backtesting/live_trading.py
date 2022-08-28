from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


# Import the backtrader platform
import backtrader as bt

# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('parameters', [5.8, 10, 5, 28]),
        ('printlog', False),
        ('progress', True),
        ('starting_price', 0),
        ('ending_price', 0),
        ('sizer_percent',99),
        ('portfolio_value', 0),
        ('live_data', False)
    )

    def notify_data(self, data, status):
        if status == data.LIVE:
            print("Live data")
            self.live_data = True

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            tm = self.datas[0].datetime.time()
            print('%s, %s, %s' % (dt.isoformat(), tm, txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        print("in init")
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.first_price = True
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

        if not self.live_data:
            return

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
        self.params.ending_price = self.dataclose[0]
        self.params.portfolio_value = self.broker.getvalue()
    


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    store = bt.stores.IBStore(host='127.0.0.1', 
                  port=7497, 
                  clientId=35)

    data = store.getdata(name="AAPL",         # Data name
                       dataname='AAPL',     # Symbol name
                       secType='STK',       # SecurityType is STOCK
                       exchange='SMART',    # Trading exchange IB's SMART exchange 
                       currency='USD'      # Currency of SecurityType
                       )

    # cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=2)

    broker = store.getbroker()

    # Set the broker
    cerebro.setbroker(broker)

    cerebro.addsizer(bt.sizers.PercentSizerInt)
    cerebro.addstrategy(TestStrategy)

    print("We made it here")
    
    cerebro.run()

    print("past run")
