import numpy as np
from tqdm import tqdm
import pandas as pd

def find_timestamp_extremum(df, df_lower_timeframe):

    df = df.copy()
    df = df.loc[df_lower_timeframe.index[0]:]
    #Set new columns
    df["low_time"] = np.nan
    df["high_time"] = np.nan

    #Loop to find out if the low or high appear first
    for i in tqdm(range(len(df) - 1)):
                  
        #Extract values from the lower timeframe
        start = df.iloc[i:i + 1].index[0]
        end = df.iloc[i + 1:i + 2].index[0]
        row_lowest_timeframe = df_lower_timeframe.loc[start:end].iloc[:-1]

        #Extract Timestamp of the max and min over the period (high time frame)
        try:
            high = row_lowest_timeframe["high"].idxmax()
            low = row_lowest_timeframe["low"].idxmin()
                  
            df.loc[start, "low_time"] = low
            df.loc[start, "high_time"] = high

        except Exception as e:
            print(e)
            df.loc[start, "low_time"] = start
            df.loc[start, "high_time"] = start

#Verify the number of extremum found
    percent_garbage_row = len(df.dropna()) / len(df) * 100
    #If percentage_garbabe_row < 95:
    print(f"WARNING: Garbage row: {'%.2f' % percent_garbage_row}%")

    df = df.iloc[:-1]

    return df

df_low_tf = pd.read_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_M30_from_2014-01-01T00-00-00Z_to_2024-03-10T00-00-00Z.csv", index_col="time", parse_dates=True)
df_high_tf = pd.read_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_H4_from_2014-01-01T00-00-00Z_to_2024-03-10T00-00-00Z.csv", index_col="time", parse_dates=True)

df = find_timestamp_extremum(df_high_tf, df_low_tf)

print(df[['high_time', 'low_time']])
df.to_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_H4_READY.csv")

