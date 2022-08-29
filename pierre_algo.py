import pandas as pd
import numpy as np

#fix table

def gradients_fct(data, window):

    SMA = data.rolling(window=window).mean()

    gradients_prov = pd.DataFrame.pct_change(SMA)
    gradients = pd.Series(gradients_prov).fillna(0)
    second_gradients = pd.Series(np.gradient(gradients))

    return gradients, second_gradients, SMA

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

        # TAKING A SHORT POSITION
        elif gradients[i] < 0 and gradients[i - 1] >= 0:
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
    if ((second_gradients[i] > 0 and gradients[i - 1] > 0 and gradients[i] > 0)
        or (second_gradients[i] > 0 and gradients[i - 1] < 0 and gradients[i] < 0)):

        profit, price_bought_at, price_short_at, i, data, sigPriceBuy, sigPriceSell, flag = buy(
            profit, price_bought_at, price_short_at, i, data, sigPriceBuy,
            sigPriceSell, flag)

        return sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit, price_bought_at, price_short_at, flag

    #sell more short or begin to sell long
    elif ((second_gradients[i] < 0 and gradients[i - 1] < 0 and gradients[i] < 0) or
        (second_gradients[i] < 0 and gradients[i - 1] > 0 and gradients[i] > 0)):

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

    for i in range(1,len(data)):
        diff = data[i - 1] - data[i]
        daily_profit.append(diff*flag_status[i])
        position.append(trade_base*flag_status[i])

    return daily_profit, position



def table_generation(data, window):

    gradients, second_gradients, SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit = inflexion_primary(data,window)
    daily_profit, position = position_array(data, flag_status, daily_profit)

    cumulative_profit = np.cumsum(daily_profit)

    print(len(data))
    print(len(gradients))
    print(len(second_gradients))
    print(len(SMA))
    print(len(sigPriceBuy))
    print(len(sigPriceSell))
    print(len(flag_status))
    print(len(position))
    print(len(daily_profit))
    print(len(cumulative_profit))

    #table = pd.DataFrame({
    #'PRICE': data, 2607
    #'GRADIENTS': gradients, 2607
    #'SECOND_GRADIENTS': second_gradients, 2607
    #'SMA': SMA, 2571
    #'BUY_SIGNALS': sigPriceBuy, 2607
    #'SELL_SIGNALS': sigPriceSell, 2571
    #'DIRECTIONAL EXPOSURE': flag_status,  2607
    #'POSITION':position, 2607
    #'DAILY PROFIT': daily_profit, 2607
    #'CUMULATIVE PROFIT': cumulative_profit 2607
    #})
    return profit #, table



def algo_call(series, window):
    data = pd.read_excel('Data/Time Series Data.xlsx', index_col='Day')
    df = data['Series {}'.format(series)]
    profit = table_generation(df, window)
    print('the profit is'+str(profit))
    return profit #,table

if __name__ == '__main__':
    algo_call(4,15)
