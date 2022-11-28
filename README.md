# TradingBot
Hello! 

This is an algorithmic trading bot that I created during the summer of 2022.
Having an interest in the field, I decided that this would be a good first step into the world of automated trading.
I decided to trade on Ethereum because of its volatility, its 24 hour trading, and because of the inherit ability to day trade it since it can't be traded on margin.
There are two main components involved in this build: The backtesting, and the live trading.


The first thing I worked on was the backtesting functionality. By leveraging the library Backtrader and Python, I was able to locally formulate and backtest strategies against historical Ethereum data using machine learning techniques.
I created a system that allows me to manually download/import historical market data or pull it from yahoo finance.
Through research, testing, and analyzing results, I decided to go with KAMA while optimizing the parameters. The struggle of not wanting to overfit my data led me to the use of sampling and breaking up my data into test and validation datasets. After running tens of thousands of iterations, I landed on my parameters and using daily tick data over hourly and other granularities.

And now, with the parameters and strategy in place, it was time to work on live trading. While I initially intended for this system to use IBKR because of
Backtrader's integration with it, it didn't end up working because of unforeseen bugs and maintenance issues. Because of that, I pivoted to using Binance.
By connecting to the Binance API, I could use the strategy previously formulated during backtesting (KAMA) to execute trades on live data.


Lastly, I created an AWS EC2 instance and uploaded this repo (plus some hidden directories) so that I can run this strategy continuously on the cloud. 


Note, I am aware of the amateurishness of this strategy, but the point of this project was just to get a sense of what its like to formulate, test, and execute a trading strategy from scratch.

PS. There are earlier commits that include a config.json file that included my api key and secret key. I have since changed them and made this repo publically available. 
PS. The main code for backtesting is found in backtesting.py and backtesting2.py. The main code for binance_bot is binance_bot.py.
