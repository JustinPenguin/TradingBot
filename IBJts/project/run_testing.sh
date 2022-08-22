#!/bin/sh

for n in {1..10}; 
do
    python3 backtesting.py False False >> sma_test.txt
done