'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.
'''

'''
Computational Investment Part I
Week-8:Homework-7::Submitted 2013.10.14
By: Frank Xia
Contact: emdyxiafan@gmail.com
'''

import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import sys
import csv


### START : read_csv_data ###
# Read port value from csv file, save in array
## PARAMS: csv-filename
## RETURN: na_port_vals (numpy array contains port vals)
def read_csv_port_vals(filename):
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    ls_port_vals = []
    for row in reader:
        ls_port_vals.append(float(row[1]))

    na_port_vals = np.zeros(len(ls_port_vals))
    for i in range(0, len(ls_port_vals)):
       na_port_vals[i] = float(ls_port_vals[i])
    return na_port_vals 
### END : read_csv_port_vals ###


def portfolio_analyzer(na_port_vals):
    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_vals = na_port_vals / na_port_vals[0]
    print(na_normalized_vals)


    # Numpy matrix of filled data values
    na_portrets = na_normalized_vals.copy()

    tsu.returnize0(na_portrets)
    port_length = len(na_portrets)
    print("Data Points: ")
    print(port_length)
    port_length = 252
    port_avg = np.average(na_portrets)
    port_div = np.std(na_portrets)
    port_sharp = math.sqrt(port_length)*port_avg/port_div

    # Estimate portfolio returns
    print("Days: ")
    print(port_length)
    print("Sharpe Ratio:")
    print(port_sharp)

    print("Stdev:")
    print(port_div)
    print("Avg Ret:") 
    print(port_avg)



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ' Usage: python',sys.argv[0],"<values-input-csv> <benchmark-index>"
        sys.exit()

    port_vals = read_csv_port_vals(sys.argv[1])

    portfolio_analyzer(port_vals)

