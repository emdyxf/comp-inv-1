'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.
'''

'''
Computational Investment Part I
Week-5:Homework-4::Submitted 2013.10.05
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
import csv
import sys


def find_events(ls_symbols, d_data):
    print "Starting Event Profiler"

    df_close = d_data['actual_close']
#    df_close = d_data['close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
        #    if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:

            if f_symprice_yest >= 5.00 and f_symprice_today < 5.0 :
        #    if f_symprice_yest >= 7.00 and f_symprice_today < 7.0 :
        #    if f_symprice_yest >= 10.00 and f_symprice_today < 10.0 :

                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


def create_orders(filename, df_events, ls_symbols, ldt_timestamps):
    df_orders = copy.deepcopy(df_events)
    writer = csv.writer(open(filename, 'wb'), delimiter=',')
    for i in (range(1, len(ldt_timestamps))):
        for s_sym in ls_symbols:
            if df_orders[s_sym].ix[ldt_timestamps[i]] == 1:
                entry_year = ldt_timestamps[i].year
                entry_month = ldt_timestamps[i].month
                entry_day = ldt_timestamps[i].day
                
                # Buy and hold 100 shares for 5 days 
                row_to_enter = [entry_year, entry_month, entry_day, s_sym, "Buy", 100]
                writer.writerow(row_to_enter)

                index_exit = i
                if i+5 <  len(ldt_timestamps)-1:
                    index_exit = i+5
                else:
                    index_exit = len(ldt_timestamps)-1
                df_orders[s_sym].ix[ldt_timestamps[index_exit]] = -1
                
                exit_year = ldt_timestamps[index_exit].year
                exit_month = ldt_timestamps[index_exit].month
                exit_day = ldt_timestamps[index_exit].day
                
                row_to_enter = [exit_year, exit_month, exit_day, s_sym, "Sell", 100]
                writer.writerow(row_to_enter)
    return df_orders



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ' Usage: python',sys.argv[0],"<orders-output-csv>"
        sys.exit()  
 
    dt_start = dt.datetime(2008, 1, 1)
    dt_last = dt.datetime(2009, 12, 30)
    dt_end= dt_last + dt.timedelta(days=1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    print "Reading Symbol..."

    dataobj = da.DataAccess('Yahoo')
#    ls_symbols = dataobj.get_symbols_from_list('sp5002008')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
#    ls_symbols.append('SPY')

    print(ls_symbols)

    print "Reading Data..."

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    print "Processing Data..."

    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    print "Proceed to Event Profiler.." 

    df_events = find_events(ls_symbols, d_data)

    print "Generate orders..."
    df_orders = create_orders(sys.argv[1], df_events, ls_symbols, d_data['actual_close'].index)

