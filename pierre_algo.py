import pandas as pd
import numpy as np

def gradients_fct(data, window):

    SMA = data.rolling(window=window).mean()
    gradients_prov = pd.DataFrame.pct_change(SMA)

    gradients = pd.Series(gradients_prov).fillna(0)
    second_gradients = pd.Series(np.gradient(gradients))

    return gradients, second_gradients, SMA

def buy(flag, sigPriceBuy, sigPriceSell):
    flag = 1
    sigPriceBuy.append('BUY')
    sigPriceSell.append(0)
    return flag, sigPriceBuy, sigPriceSell


def sell(flag, sigPriceBuy, sigPriceSell):
    flag = -1
    sigPriceBuy.append(0)
    sigPriceSell.append('SELL')
    return flag, sigPriceBuy, sigPriceSell

def inflexion_primary(data, window):

    gradients, second_gradients,SMA = gradients_fct(data,window)

    #PARAMETERS
    #flag = 1: long position, flag = -1: short position, flag = 0: no position

    sigPriceBuy = []
    sigPriceSell = []
    flag = 0
    flag_status = []
    daily_profit = []
    profit = 0
    trade_base = 100000  #100,000

    ###########BASE PROFIT OVERALL
    for i in range(len(data)):

        flag_status.append(flag)

        # TAKING A LONG POSITION
        if gradients[i] > 0 and gradients[i - 1] <= 0:

            #From nothing to long
            if flag == 0:
                price_bought_at = data[i]
                buy(flag, sigPriceBuy, sigPriceSell)

            #From short to a long
            elif flag == -1:
                profit += price_short_at - data[i]
                price_bought_at = data[i]
                buy(flag, sigPriceBuy, sigPriceSell)

            #from long to more long
            elif flag == 1:
                inflexion_secondary(data, gradients, second_gradients,
                                    sigPriceBuy, SMA, sigPriceSell, profit,
                                    flag_status, daily_profit)

                pass

        # TAKING A SHORT POSITION
        elif gradients[i] < 0 and gradients[i - 1] >= 0:

            #from nothing to a short
            if flag == 0:
                price_short_at = data[i]
                sell(flag, sigPriceBuy, sigPriceSell)

            #from long to a short
            elif flag == 1:
                profit += data[i] - price_bought_at
                price_short_at = data[i]
                sell(flag, sigPriceBuy, sigPriceSell)

            #from short to more short
            elif flag == -1:
                inflexion_secondary(data, gradients, second_gradients,
                                    sigPriceBuy, SMA, sigPriceSell, profit,
                                    flag_status, daily_profit)
                pass

        else:
            sigPriceBuy.append(0)
            sigPriceSell.append(0)

    return gradients, second_gradients, sigPriceBuy,SMA, sigPriceSell, profit, flag_status, daily_profit

def inflexion_secondary(data, gradients, second_gradients, sigPriceBuy, SMA, sigPriceSell, profit, flag_status, daily_profit):

    for i in range(len(data)):
        if second_gradients[i] > 0 and gradients[i - 1] > 0 and gradients[i] > 0:
            sigPriceBuy.append('BUY')
            sigPriceSell.append(0)
            pass

        elif second_gradients[i] < 0 and gradients[i - 1] < 0 and gradients[i] < 0:
            sigPriceBuy.append(0)
            sigPriceSell.append('SELL')

        else:
            sigPriceBuy.append(0)
            sigPriceSell.append(0)

        pass

    return sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit


def position_array(data, flag_status, daily_profit):

    position = []
    trade_base = 100000 #100,000

    current_position = 0
    for i in range(0, len(data)):

        if flag_status[i] == 0:
            daily_profit.append(0)
            position.append(0)

        if flag_status[i] == 1:
            daily_profit.append(data[i] - data[i - 1])
            position.append(trade_base)

        if flag_status[i] == -1:
            daily_profit.append(data[i - 1] - data[i])
            position.append(-trade_base)

    return position



def table_generation(data, window):

    gradients, second_gradients, SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit = inflexion_primary(data,window)
    position = position_array(data, flag_status, daily_profit)

    cumulative_profit = np.cumsum(daily_profit)

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
        'CUMULATIVE PROFIT': cumulative_profit
    })
    return table, profit



def algo_call(series, window):
    data = pd.read_excel('Data/Time Series Data.xlsx', index_col='Day')
    df = data['Series {}'.format(series)]
    table, profit = table_generation(df, window)
    print(profit)
    return table, profit

if __name__ == '__main__':
    algo_call(13,15)
