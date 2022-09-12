import pandas as pd
import numpy as np
from openpyxl import load_workbook
import matplotlib.pyplot as plt
#fix table and length of arrays
#add the output compatibility

def gradients_fct(data, window):

    SMA = data.rolling(window=window).mean()

    gradients_prov = pd.DataFrame.pct_change(SMA)
    gradients = pd.Series(gradients_prov).fillna(0)
    second_gradients = pd.Series(np.gradient(gradients))

    return gradients, second_gradients, SMA

def buy_and_sell_prices(table):
    table['buy_price'] = [x.PRICE if x.BUY_SIGNALS == 'BUY' else 0 for index, x in table.iterrows()]
    table['sell_price'] = [x.PRICE if x.SELL_SIGNALS == 'SELL' else 0 for index, x in table.iterrows()]
    return table

def buy(profit, price_bought_at,price_short_at, i, data, sigPriceBuy, sigPriceSell, flag=1):

    if flag<0:
        profit += data[i] - sum(price_short_at)/len(price_short_at)

    flag += 1

    sigPriceBuy.append('BUY')
    sigPriceSell.append(0)

    price_bought_at = update_long_price(i,price_bought_at, data)

    return profit, price_bought_at, price_short_at, i, data, sigPriceBuy, sigPriceSell, flag

def sell(profit, i,price_bought_at, price_short_at, data, sigPriceBuy, sigPriceSell, flag=-1):

    if flag>0:
        profit += sum(price_bought_at)/len(price_bought_at) - data[i]

    flag += -1

    sigPriceBuy.append(0)
    sigPriceSell.append('SELL')

    price_short_at = update_short_price(i,price_short_at, data)

    return profit, i, price_bought_at, price_short_at, data, sigPriceBuy, sigPriceSell, flag

def update_short_price(i,price_short_at, data):
    price_short_at.append(data[i])
    if len(price_short_at)>5:
        price_short_at = price_short_at[1:]
    return price_short_at

def update_long_price(i,price_bought_at, data):
    price_bought_at.append(data[i])
    if len(price_bought_at)>5:
        price_bought_at = price_bought_at[1:]
    return price_bought_at

def inflexion_primary(data, window):

    gradients, second_gradients,SMA = gradients_fct(data,window)

    sigPriceBuy = []
    sigPriceSell = []
    flag = 0
    flag_status = []
    daily_profit = [0]
    profit = 0
    price_short_at=[]
    price_bought_at=[]

    ###########BASE PROFIT OVERALL
    for i in range(len(data)):

        flag_status.append(flag)

        # TAKING A LONG POSITION
        if gradients[i] > 0 and gradients[i-1] <= 0:

            #From nothing to long
            if flag == 0:
                profit, price_bought_at, price_short_at, i, data, sigPriceBuy, sigPriceSell, flag = buy(
                    profit, price_bought_at, price_short_at,i, data, sigPriceBuy,
                    sigPriceSell, flag)

            #From short to a long
            elif flag <= -1 :
                profit, price_bought_at, price_short_at, i, data, sigPriceBuy, sigPriceSell, flag = buy(
                    profit, price_bought_at, price_short_at, i, data, sigPriceBuy,
                    sigPriceSell, flag)
            elif flag >0 :
                sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag = inflexion_secondary(
                    i, data, gradients, second_gradients, sigPriceBuy, SMA,
                    sigPriceSell, profit, flag_status, daily_profit,
                    price_short_at, price_bought_at, flag)

        # TAKING A SHORT POSITION
        elif gradients[i] < 0 and gradients[i-1] >= 0:

            #from nothing to a short
            if flag == 0:
                profit, i, price_bought_at, price_short_at, data, sigPriceBuy, sigPriceSell, flag = sell(
                    profit, i, price_bought_at, price_short_at, data, sigPriceBuy,
                    sigPriceSell, flag)

            #from long to a short
            elif flag >= 1:
                profit, i, price_bought_at, price_short_at, data, sigPriceBuy, sigPriceSell, flag = sell(
                    profit, i, price_bought_at, price_short_at, data, sigPriceBuy,
                    sigPriceSell, flag)
            elif flag <0:

                sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag = inflexion_secondary(
                    i, data, gradients, second_gradients, sigPriceBuy, SMA,
                    sigPriceSell, profit, flag_status, daily_profit,
                    price_short_at, price_bought_at, flag)

            #from short to more short
        elif flag <= -1 or flag >= 1:
            sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag = inflexion_secondary(
                i, data, gradients, second_gradients, sigPriceBuy, SMA,
                sigPriceSell, profit, flag_status, daily_profit,
                price_short_at, price_bought_at, flag)

        else:

            sigPriceBuy.append(0)
            sigPriceSell.append(0)

    return gradients, second_gradients,SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit

def inflexion_secondary(i, data, gradients, second_gradients, sigPriceBuy,
                        SMA, sigPriceSell, profit, flag_status, daily_profit,
                        price_short_at, price_bought_at, flag):

    #buy more long or begin to sell short
    if (((second_gradients[i] > 0 and gradients[i-1] >= 0 and gradients[i] > 0)
        or (second_gradients[i] > 0 and gradients[i-1] <= 0 and gradients[i] < 0))and flag<5):

        profit, price_bought_at, price_short_at, i, data, sigPriceBuy, sigPriceSell, flag = buy(
            profit, price_bought_at, price_short_at, i, data, sigPriceBuy,
            sigPriceSell, flag)

        return sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag

    #sell more short or begin to sell long
    elif (((second_gradients[i] < 0 and gradients[i-1] <= 0 and gradients[i] < 0) or
        (second_gradients[i] < 0 and gradients[i-1] >= 0 and gradients[i] > 0))and flag>-5):

        profit, i, price_bought_at, price_short_at, data, sigPriceBuy, sigPriceSell, flag = sell(
            profit, i, price_bought_at, price_short_at, data, sigPriceBuy,
            sigPriceSell, flag)

        return sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag

    else:
        sigPriceBuy.append(0)
        sigPriceSell.append(0)
        return sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag


def position_array(data, flag_status, daily_profit):

    position = [0]
    trade_base = 100000 #100,000
    trades = [0]

    for i in range(1, len(flag_status)):
        diff = flag_status[i - 1] - flag_status[i]
        trades.append(trade_base*diff)


    for i in range(1,len(data)):
        diff = data[i-1] - data[i]
        daily_profit.append(diff*flag_status[i])
        position.append(trade_base*flag_status[i])

    return daily_profit, position, trades



def table_generation(data, window):

    gradients, second_gradients, SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit = inflexion_primary(data,window)
    daily_profit, position, trades = position_array(data, flag_status, daily_profit)

    cumulative_profit = np.cumsum(daily_profit)

    #print(len(data))
    #print(len(gradients))
    #print(len(second_gradients))
    #print(len(SMA))
    #print(len(sigPriceBuy))
    #print(len(sigPriceSell))
    #print(len(flag_status))
    #print(len(position))
    #print(len(daily_profit))
    #print(len(cumulative_profit))

    table = pd.DataFrame({
    'PRICE': data,
    'GRADIENTS': gradients,
    'SECOND_GRADIENTS': second_gradients,
    'SMA': SMA,
    'BUY_SIGNALS': sigPriceBuy,
    'SELL_SIGNALS': sigPriceSell,
    'DIRECTIONAL EXPOSURE': flag_status,
    'POSITION':position,
    'DAILY PROFIT': daily_profit,
    'CUMULATIVE PROFIT': cumulative_profit,
    'TRADES':trades
    })

    #table = buy_and_sell_prices(table)
    table['buy_price'] = [x.PRICE if x.BUY_SIGNALS == 'BUY' else np.nan for index, x in table.iterrows()]
    table['sell_price'] = [x.PRICE if x.SELL_SIGNALS == 'SELL' else np.nan for index, x in table.iterrows()]
    return profit, table, sigPriceBuy, sigPriceSell



def algo_call(series, window):

    #data = pd.read_excel('Data/Time Series Data.xlsx', index_col='Day')

    data = pd.read_excel("Test Bed V2.xlsm", header=1, usecols=['Series 13'])

    #df = pd.DataFrame(data_test_bed['Select series:']).iloc[1:, :]
    df = data['Series {}'.format(series)]

    #print(type(data))
    #print(type(data_test_bed))

    profit,table,sigPriceBuy,sigPriceSell = table_generation(df, window)
    print('the profit is'+str(profit*100000))

    return profit, table, sigPriceBuy, sigPriceSell

# write to excel
#load excel file
def to_excel(trades):

    workbook = load_workbook(filename="Test Bed V2.xlsm",read_only=False, keep_vba=True)
    sheet = workbook.active

    sheet['AV1']=13

    for i in np.arange(4, trades.index[-2] + 2):
        edit = 'AU' + str(int(i))
        sheet[edit] = trades['TRADES'][i - 2]
    workbook.save(filename="Test Bed V2.xlsm")

if __name__ == '__main__':
    profit,table, sigPriceBuy, sigPriceSell= algo_call(13,15)
    to_excel(table)
