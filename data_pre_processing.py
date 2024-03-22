import ta
import pandas as pd
import numpy as np



def sma(df, col, n):
    df[f"SMA_{n}"] = ta.trend.SMAIndicator(df[col], int(n)).sma_indicator()
    return df


def rsi(df, col, n):
    df["RSI"] = ta.momentum.RSIIndicator(df[col], int(n)).rsi()
    return df

df = pd.read_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_M30_from_2014-01-01T00-00-00Z_to_2024-03-10T00-00-00Z.csv")

df = sma(df, "close", 30)
df = rsi(df, "close", 14)
print(df)