#!/usr/bin/env python
# coding: utf-8

# In[669]:


# imports 
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from datetime import datetime
from openpyxl import load_workbook


# In[670]:


# get old price data
def importer():
    df = pd.read_excel('Time Series Data.xlsx', index_col = 'Day')
    df = 100*df['Series 28'][0::]/df['Series 28'].iloc[-1]

    # get new price data
    test = pd.read_excel('Test Bed V2.xlsm', usecols='AC', header=1)
    test = test['Series 28']
    
    return df, test


# In[671]:


def tradyboi(df, data, window_mean=15, upper_bound=0.1, lower_bound=0, cap_bound=0.5,             trade_size_sell=100000, trade_size_buy=50000): 

    # data - list with price data
    # window_mean - integer used in mean window
    # upper_bound - float used to find sell criteria
    # lower_bound - float used to find buy criteria
    # cap_bound - float used to find cap of buying 
    # trade_size_sell - integer for incremental amount to sell
    # trade_size_buy - integer for incremental amount to buy
    
    # constraints
    max_cap = 500000
    position = 0
    
    # create full SMA
    SMA = (df[-window_mean+2::]).append(data).rolling(window=window_mean).mean()[window_mean-2::]
    cap = (df[-200+2::]).append(data).rolling(window=200).mean()[200-2::] + cap_bound*df.std()
    upper_bounds = SMA + upper_bound*df.std()
    lower_bounds = SMA - lower_bound*df.std()
    
    # generating signals
    sigPriceBuy = []
    sigPriceSell = []
    run_pos = []
    trade = []
      
    for i in range(int(data.index[0]), int(data.index[-1]+1)):
        # Touch of lower bound = close sell and build long position until max trade reached
        if (data[i]<lower_bounds[i]) and (position<max_cap) and (data[i]<cap[i]):
            sigPriceBuy.append(data[i])
            sigPriceSell.append(np.nan)
            run_pos.append(position)
            position += trade_size_buy
            trade.append(trade_size_buy)
            
        elif (data[i]>upper_bounds[i]) and (position>0) and (data[i]-data[i-1]>0):
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(data[i])
            run_pos.append(position)
            if position >= trade_size_sell:
                position -= trade_size_sell
                trade.append(-trade_size_sell)
            else:
                position -= trade_size_buy
                trade.append(-trade_size_buy)

        else: 
            run_pos.append(position)
            sigPriceBuy.append(np.nan)
            sigPriceSell.append(np.nan)
            trade.append(np.nan)

    return (sigPriceBuy, sigPriceSell, run_pos, trade)


# In[672]:


# Placing Trade
def exceler(bsdata):
    
    # format outputs
    trades = pd.DataFrame(test.index)
    trades['trades'] = buy_sell_data[3]

    # write to excel
    #load excel file
    workbook = load_workbook(filename="Test Bed V2.xlsm", read_only=False, keep_vba=True)
 
    #open workbook
    sheet = workbook.active
 
    sheet['AH1'] = 28
    sheet['AO1'] = 0
    sheet['AV1'] = 0

    #modify the desired cell
    for i in np.arange(3,trades.reset_index().index[-1]+4):
        edit1 = 'AG'+str(int(i))
        sheet[edit1] = trades.iloc[i-3, 1]
 
    # save the file
    workbook.save(filename="Test Bed V2.xlsm")


# In[674]:


if __name__ == "__main__": 
    df, test = importer()
    buy_sell_data = tradyboi(df, test)
    exceler(buy_sell_data)


# In[ ]:




