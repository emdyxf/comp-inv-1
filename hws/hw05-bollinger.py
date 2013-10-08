'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.
'''

'''
Computational Investment Part I
Week-7:Homework-5::Submitted 2013.10.08
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



### START : write_csv_data ###
# Write dataframe into csv file
## PARAMS: csv-filename, df_bollinger_val (Bollinger values with timestamps)
## RETURN: N.A.
def write_csv_data(filename, df_bollinger_val):
   writer = csv.writer(open(filename, 'wb'), delimiter=',')
   for row_index in df_bollinger_val.index:
        row_to_enter = [row_index, float(df_bollinger_val[row_index])]
        writer.writerow(row_to_enter)
### END : write_csv_data ###


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ' Usage: python',sys.argv[0],"<symbol-name> <output-csv-file>"
        sys.exit()   

    ls_symbols = [sys.argv[1]]

    # Process market data
    print "Processing historical market data..."
    # DATE RANGE: 2010.01.01 - 2010.12.31
    dt_start = dt.datetime(2010, 1, 1)
    dt_last = dt.datetime(2010, 12, 31)
    dt_end= dt_last + dt.timedelta(days=1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    df_price = d_data['close']   
    ldt_timestamps = df_price.index

    df_bollinger = copy.deepcopy(df_price)

    df_bollinger['_SMA'] = float(0.0)
    df_bollinger['_SMA'] = pd.rolling_mean(df_bollinger[ls_symbols], 20)

    df_bollinger['_STD'] = float(0.0)
    df_bollinger['_STD'] = pd.rolling_std(df_bollinger[ls_symbols], 20)
  
    df_bollinger['_IND'] = float(0.0)
    for i in range(0, len(ldt_timestamps)):
        df_bollinger['_IND'].ix[ldt_timestamps[i]] = (df_bollinger[ls_symbols].ix[ldt_timestamps[i]] - df_bollinger['_SMA'].ix[ldt_timestamps[i]]) / df_bollinger['_STD'].ix[ldt_timestamps[i]]
 

    # Write Bollinger value to csv-file
    write_csv_data(sys.argv[2], df_bollinger['_IND'])
