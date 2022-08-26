import pandas as pd
import numpy as np

def gradients_fct(data, window):

    SMA = data.rolling(window=window).mean()
    gradients_prov = pd.DataFrame.pct_change(SMA)

    gradients = pd.Series(gradients_prov).fillna(0)
    second_gradients = pd.Series(np.gradient(gradients))

    return gradients, second_gradients

def rolling_averages_inflexions_comp(data, window):

    gradients, second_gradients = gradients_fct(data,window)

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

        #We buy/sell at the close of the next day hence begin the day with previous flag
        flag_status.append(flag)

        #if we reach the end of the dataframe either sell the long or buy the short at current price
        if i == len(data) - 1:

            #if long go back to nothing
            if flag == 1:

                #from long to no position
                sigPriceBuy.append(0)
                sigPriceSell.append('SELL')

                flag = 0

                #daily_profit.append(data[i])
                profit += data[i] - price_bought_at

            #if short go back to nothing
            elif flag == -1:

                sigPriceBuy.append('BUY')
                sigPriceSell.append(0)

                flag = 0

                #daily_profit.append(data[i])
                profit += price_short_at - data[i]

        #iterate through all the other days and find profit
        else:
            # TAKING A LONG POSITION
            if gradients[i] > 0 and gradients[i - 1] <= 0:

                #From nothing to long
                if flag == 0:
                    price_bought_at = data[i]
                    flag = 1
                    sigPriceBuy.append('BUY')
                    sigPriceSell.append(0)

                #From short to a long
                elif flag == -1:
                    profit += price_short_at - data[i]
                    price_bought_at = data[i]
                    flag = 1
                    sigPriceBuy.append('BUY')
                    sigPriceSell.append(0)

                #from long to long - NO CHANGE
                elif flag == 1:
                    sigPriceBuy.append(0)
                    sigPriceSell.append(0)

                    pass

            # TAKING A SHORT POSITION
            elif gradients[i] < 0 and gradients[i - 1] >= 0:

                #from nothing to a short
                if flag == 0:
                    price_short_at = data[i]
                    flag = -1
                    sigPriceBuy.append(0)
                    sigPriceSell.append('SELL')

                #from short to short - NO CHANGE
                elif flag == -1:
                    sigPriceBuy.append(0)
                    sigPriceSell.append(0)
                    pass

                #from long to a short
                elif flag == 1:
                    profit += data[i] - price_bought_at
                    price_short_at = data[i]
                    flag = -1
                    sigPriceBuy.append(0)
                    sigPriceSell.append('SELL')
            else:
                sigPriceBuy.append(0)
                sigPriceSell.append(0)

    return gradients, second_gradients, SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit


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

    gradients, second_gradients, SMA, sigPriceBuy, sigPriceSell, profit, flag_status, daily_profit = rolling_averages_inflexions_comp(data,window)
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
