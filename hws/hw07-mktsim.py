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
# Read orders in csv file, determine all the ordered dates and symbols
## PARAMS: csv-filename, (empty)list_dates, (empty)list_syms
## RETURN: list_syms(with param list), list_dates(with param list)
def read_csv_data(filename, list_dates, list_syms):
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    for row in reader:
        this_date = dt.datetime(int(row[0]),int(row[1]),int(row[2]),16)
        list_dates.append(this_date)
        list_syms.append(row[3])
### END : read_csv_data ###


### START : write_csv_data ###
# Write time-series into csv file
## PARAMS: csv-filename, ts_fund (port fund in timeseris format
## RETURN: N.A.
def write_csv_data(filename, ts_fund):
   writer = csv.writer(open(filename, 'wb'), delimiter=',')
   for row_index in ts_fund.index:
        row_to_enter = [row_index, float(ts_fund[row_index])]
        writer.writerow(row_to_enter)
### END : write_csv_data ###

### START: create_trade_matrix ###
## Read order in csv file and create trade matrix to capture movement
### PARAMS: d_data (market data), csv_orders(csv-filename)
### RETURN: df_trade [Symbol, Time, Shares (Buy: +ve; Sell: -ve)
def create_trade_matrix(d_data, csv_orders):
    df_close = d_data['close']
#    df_close = d_data['actual_close']

    # Creating an empty dataframe
    df_trades = copy.deepcopy(df_close)
    df_trades = df_trades * 0

    # Time stamps
    ldt_timestamps = df_close.index

    reader = csv.reader(open(csv_orders, 'rU'), delimiter=',')
    for row in reader:
        trade_timestamp = dt.datetime(int(row[0]),int(row[1]),int(row[2]),16)
        
        trade_symbol = row[3]
        trade_side = row[4]
        trade_shares = row[5]

        for i in range(0, len(ldt_timestamps)):
            if trade_timestamp == ldt_timestamps[i]:
                if trade_side == "Buy":
                    df_trades[trade_symbol].ix[ldt_timestamps[i]] = df_trades[trade_symbol].ix[ldt_timestamps[i]] + int(trade_shares)
                elif trade_side == "Sell":
                    df_trades[trade_symbol].ix[ldt_timestamps[i]] = df_trades[trade_symbol].ix[ldt_timestamps[i]] - int(trade_shares)
    
    return df_trades
### END : create_trade_matrix ### 


### START: create_holding_matrix ###
## Read order from trade matrix to calculate holding values
### PARAMS: d_data (market data), df_trades (trade entries), ls_symbols (traded symbols),
### RETURN: df_holdings (holding shares and port values)
def create_holding_matrix(d_data, df_trades, ls_symbols):
    df_close = d_data['close']
    ldt_timestamps = df_close.index
    df_holdings = df_trades * 0
    df_holdings['_VALUE'] = float(0.0)
      
    for i in range(0, len(ldt_timestamps)):
        for s_sym in ls_symbols:
            if i == 0:
                holding_prior = 0
            else:
                holding_prior = df_holdings[s_sym].ix[ldt_timestamps[i-1]] 
            df_holdings[s_sym].ix[ldt_timestamps[i]] = holding_prior + df_trades[s_sym].ix[ldt_timestamps[i]]
            
            holding_shares = df_holdings[s_sym].ix[ldt_timestamps[i]]
            holding_price = df_close[s_sym].ix[ldt_timestamps[i]]
            df_holdings['_VALUE'].ix[ldt_timestamps[i]] = df_holdings['_VALUE'].ix[ldt_timestamps[i]] + float(holding_shares) * float(holding_price)

    return df_holdings
### END : create_holding_matrix


### START : balance_cash_acct ###
# Read order in trade matrix and update cash account
## PARAMS: d_data (market data), df_trades (trade entries), ls_symbols (traded symbols), int_start_bal (starting balance)
## RETURN: ts_balance (Timeseries of cash balance)
def balance_cash_acct (d_data, df_trades, ls_symbols, int_start_bal):    
    df_close = d_data['close']
    df_close['_CASH'] = float(0.0)
    ts_cash = df_close['_CASH']
    ts_cash[0] = float(int_start_bal)

    ldt_timestamps = df_close.index
 
    for i in range(0, len(ldt_timestamps)):
        d_movement_intraday = float(0.0);
        for s_sym in ls_symbols:
            if df_trades[s_sym].ix[ldt_timestamps[i]] != 0:
                traded_shares = df_trades[s_sym].ix[ldt_timestamps[i]]
                traded_price = df_close[s_sym].ix[ldt_timestamps[i]]
                d_movement_intraday = d_movement_intraday - float(traded_shares) * float(traded_price)
        if i == 0:
            d_cash_prior = float(int_start_bal)
        else:       
            d_cash_prior = float(ts_cash[i-1])
        ts_cash[i] = float(d_cash_prior) + float(d_movement_intraday)
    return ts_cash
### END : balance_cash_acct ###


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print ' Usage: python',sys.argv[0],"<starting-cash> <orders-input-csv> <values-output-csv>"
        sys.exit()   

    # Get Date List and Symbol List
    ls_dates = []
    ls_syms_data = []
    read_csv_data(sys.argv[2], ls_dates, ls_syms_data)
    ls_symbols = list(set(ls_syms_data))

    # Process market data
    print "Processing historical market data..."
    # PORT: 2008.01.01 - 2009.12.31
    dt_start = dt.datetime(2008, 1, 1)
    dt_last = dt.datetime(2009, 12, 30)
    dt_end= dt_last + dt.timedelta(days=1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')

#    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    
    # Create Trade Matrix
    print "++++ Creating trade matrix..."
    df_trade_matrix = create_trade_matrix(d_data, sys.argv[2])

    # Create Holding Matrix
    print "++++ Creating holding matrix..."
    df_holding_matrix = create_holding_matrix(d_data, df_trade_matrix, ls_symbols)
    
    # Process cash balance with orders
    print "++++ Balancing cash..."
    cash_balance = balance_cash_acct (d_data, df_trade_matrix, ls_symbols, sys.argv[1])    

    print "++++ Calculating portfolio worth..."
    port_value = cash_balance
    ldt_timestampe = port_value.index
    for i in range(0, len(ldt_timestamps)):
        port_value.ix[ldt_timestamps[i]] = port_value.ix[ldt_timestamps[i]] + float(df_holding_matrix['_VALUE'].ix[ldt_timestamps[i]])
    print port_value

    # Write port_value to csv-file
    write_csv_data(sys.argv[3], port_value)
