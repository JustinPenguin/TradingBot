#!/bin/sh

rm -rf results2.txt
for n in {1..5}; 
do
    python3 backtesting2.py False False >> results2.txt
done

rm -rf testing_results.txt
python3 testing_parameters.py False True >> testing_results.txt