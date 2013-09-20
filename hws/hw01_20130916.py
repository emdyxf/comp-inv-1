'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 24, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Example tutorial code.
'''


'''
Coursera :  Computational Investment I
Week-3:Homework-1::Submitted 2013.09.16
By: Fan Xia
Contact: emdyxiafan@gmail.com
'''


# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math as math

print "Pandas Version", pd.__version__


def main():
    ''' Main Function'''

    valid_alloc = [0.0,0.1,0.2,0.3,0.4,0.5,0.5,0.7,0.8,0.9,1.0]

# Sample 01
#    ls_symbols = ["AAPL", "GLD", "GOOG", "XOM"]
#    optimal_alloc = [0.4, 0.4, 0.0, 0.2]
#    dt_start = dt.datetime(2011, 1, 1)
#    dt_end = dt.datetime(2011, 12, 31)

# Sample: 02
#    ls_symbols = ["AXP", "HPQ", "IBM", "HNZ"]
#    optimal_alloc = [0.0, 0.0, 0.0, 1.0]
#    dt_start = dt.datetime(2010, 1, 1)
#    dt_end = dt.datetime(2010, 12, 31)

# HW1:
    ls_symbols = ["AAPL", "GOOG", "IBM", "MSFT"]
    optimal_alloc = [0.0, 0.0, 0.0, 0.0]
    optimal_sharp_ratio = 0.0

# HW1: Qn1
#    dt_start = dt.datetime(2010, 1, 1)
#    dt_end = dt.datetime(2010, 12, 31)

# HW1: Qn2
    dt_start = dt.datetime(2011, 1, 1)
    dt_end = dt.datetime(2011, 12, 31)


    # We need closing prices so the timestamp should be hours=16
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    #c_dataobj = da.DataAccess('Yahoo')
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
#    print(d_data['close'].values)

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    # Numpy matrix of filled data values
    na_rets = na_normalized_price.copy()

    for i in valid_alloc:
      for j in valid_alloc:
        for k in valid_alloc:
          if i+j+k > 1:
            continue
          else:
            this_alloc = [i,j,k,1-i-j-k]
#            print(this_alloc)
            na_portrets = np.sum(na_rets * this_alloc, axis=1)
            tsu.returnize0(na_portrets)
            port_length = len(na_portrets)
            port_avg = np.average(na_portrets)
            port_div = np.std(na_portrets)
            port_sharp = math.sqrt(port_length)*port_avg/port_div
            if port_sharp > optimal_sharp_ratio:
              print(this_alloc)
              print "Curr SharpRatio:", port_sharp
              print "> Opt SharpRatio:", optimal_sharp_ratio
              optimal_alloc = this_alloc
              optimal_sharp_ratio = port_sharp


    # Estimate portfolio returns
    na_portrets = np.sum(na_rets * optimal_alloc, axis=1)
    tsu.returnize0(na_portrets)

    na_cumret = np.sum(na_normalized_price * optimal_alloc, axis=1)

    port_length = len(na_portrets) 
    port_avg = np.average(na_portrets)
    port_div = np.std(na_portrets)
    port_sharp = math.sqrt(port_length)*port_avg/port_div

    print "Optimal Alloc: ", optimal_alloc
    print("Days: ")
    print(port_length)
    print("Sharp Ratio:")
    print(port_sharp)

    print("Stdev:")
    print(port_div)
    print("Avg Ret:") 
    print(port_avg)
    print("Cum Ret:")
    print(na_cumret[port_length-1])

if __name__ == '__main__':
    main()
