'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.
'''

'''
Computational Investment Part I
Week-8:Homework-6::Submitted 2013.10.14
By: Frank Xia
Contact: emdyxiafan@gmail.com
'''

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import csv
import sys


def find_events(ls_symbols, df_bollinger_matrix):
    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_bollinger_matrix)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_bollinger_matrix.index
    
    int_event_count = 0

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_bollinger_today = df_bollinger_matrix[s_sym].ix[ldt_timestamps[i]]
            f_bollinger_yest = df_bollinger_matrix[s_sym].ix[ldt_timestamps[i - 1]]
            f_bollinger_spy = df_bollinger_matrix['SPY'].ix[ldt_timestamps[i]]
 

            #if f_bollinger_today <= -2.00 and f_bollinger_yest >= -2.00 and f_bollinger_spy >= 1.0 :
            if f_bollinger_today < -2.00 and f_bollinger_yest >= -2.00 and f_bollinger_spy >= 1.3 :
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                int_event_count = int_event_count + 1

    print "Total ",int_event_count,"Events found!"
    return df_events


def calculate_bollinger_values(d_data, ls_symbols, ldt_timestamps):
    df_price = d_data['close']
    df_bollinger_matrix = copy.deepcopy(df_price) * 0.0

    for s_sym in ls_symbols:
        df_bollinger =  copy.deepcopy(df_price[s_sym])
        df_bollinger_sma = copy.deepcopy(df_bollinger) * 0.0
        df_bollinger_sma = pd.rolling_mean(df_bollinger, 20)
        df_bollinger_std = copy.deepcopy(df_bollinger) * 0.0
        df_bollinger_std = pd.rolling_std(df_bollinger, 20)
        for i in range(0, len(ldt_timestamps)):
            df_bollinger_matrix[s_sym].ix[ldt_timestamps[i]] = (df_bollinger.ix[ldt_timestamps[i]] - df_bollinger_sma.ix[ldt_timestamps[i]]) / df_bollinger_std.ix[ldt_timestamps[i]]
   
    return df_bollinger_matrix


if __name__ == '__main__':
 
    dt_start = dt.datetime(2008, 1, 1)
    dt_last = dt.datetime(2009, 12, 30)
    dt_end= dt_last + dt.timedelta(days=1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    print "Reading Symbol..."

    dataobj = da.DataAccess('Yahoo')
#    ls_symbols = dataobj.get_symbols_from_list('sp5002008')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')

    print(ls_symbols)

    print "Reading Data..."

#    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    print "Processing Data..."

    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    print "Calculating Bollinger Value..."
    df_bollinger_matrix = calculate_bollinger_values(d_data, ls_symbols, ldt_timestamps)

    print "Proceed to Event Profiler.." 
    df_events = find_events(ls_symbols, df_bollinger_matrix)

    print "Creating Study..."
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
