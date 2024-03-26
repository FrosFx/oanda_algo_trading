import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


class Backtest:

    #Verify % profitable month


    def __init__(self, data, TradingStrategy, parameters, run_directly=False, title=None):
        #Set parameters
        self.TradingStrategy = TradingStrategy(data, parameters)
        self.start_date_backtest = self.TradingStrategy.start_date_backtest
        self.data = data.loc[self.start_date_backtest:]

        if "returns" not in self.data.columns:
            self.data["returns"] = 0
        if "duration" not in self.data.columns:
            self.data["duration"] = 0
        if "buy_count" not in self.data.columns:
            self.data["buy_count"] = 0
        if "sell_count" not in self.data.columns:
            self.data["sell_count"] = 0


        self.count_buy = 0
        self.count_sell = 0
        self.entry_trade_time = None
        self.exit_trade_time = None

        if run_directly:
            self.get_backtest(title)

    def run(self):
        self.data_high_time = pd.to_datetime(self.data.high_time)
        self.data_low_time = pd.to_datetime(self.data.low_time)

        for current_time in tqdm(self.data.index):
            
            #Open a position
            entry_signal = self.TradingStrategy.get_entry_signal(current_time)
            self.entry_trade_time = self.TradingStrategy.entry(current_time)
            self.data.loc[current_time, "buy_count"] = 1 if entry_signal == 1 else 0
            self.data.loc[current_time, "sell_count"] = 1 if entry_signal == -1 else 0

            #Sell a position
            position_return = self.TradingStrategy.get_exit_signal(current_time)
            self.exit_trade_time = self.TradingStrategy.exit_signal(current_time)

            #Store position return
            if position_return != 0:
                self.data.loc[current_time, "returns"] = position_return
                self.data.loc[current_time, "duration"] = (self.exit_trade_time - self.entry_trade_time).total_seconds()

    
    def get_vector_metrics(self):
        #Compute cumulative returns
        self.data["cumulative_returns"] = self.data["returns"].cumsum()

        #Compute max of the cumsum period
        running_max = np.maximum.accumulate(self.data["cumulative_returns"] + 1)

        #Compute drawdown
        self.data["drawdown"] = (self.data["cumulative_returns"] + 1) / running_max - 1


    def display_graphs(self, title=None):
        #Compute cumulative returns and drawdown
        self.get_vector_metrics()

        cum_ret = self.data["cumulative_returns"]
        drawdown = self.data["drawdown"]

        plt.rc('font', weight='bold', size=12)

        fig, (cum, dra) = plt.subplots(2, 1, figsize=(15, 7))
        plt.setp(cum.spines.values(), color="#ffffff")
        plt.setp(dra.spines.values(), color="#ffffff")

        if title is None:
            fig.subtitle("Overview of the Strategy", fontsize=18, fontweight='bold')
        else:
            fig.subtitle(title, fontsize=18, fontweight='bold')

        cum.plot(cum_ret * 100, color="#569878", linewidth=1.5)
        cum.fill_between(cum_ret.index, cum_ret * 100, 0,
                         cum_ret >= 0, color="#569878", alpha=0.3)
        cum.axhline(0, color = "#569878")
        cum.grid(axis='y', color='#505050', linestyle='--', linewidth=1, alpha=0.5)
        cum.set_ylabel("Cumulative Returns (%)", fontsize=15, fontweight='bold')

        #Put the drawdown
        dra.plot(drawdown.index, drawdown * 100, color="#C04E4E", alpha=0.5, linewidth=0.5)
        cum.set_ylabel("Drawdown (%)", fontsize=15, fontweight='bold')
        dra.fill_between(drawdown.index, drawdown * 100, 0,
                         drawdown * 100 <= 0, color="#C04E4E", alpha=0.3)
        dra.grid(axis='y', color='#505050', linestyle='--', linewidth=1, alpha=0.5)
        dra.set_ylabel("Drawdown (%)", fontsize=15, fontweight='bold')

        plt.show()


    def display_metrics(self):
        #Compute cumulative returns and drawdown
        self.get_vector_metrics()

        #Average trade duration
        try:
            seconds = self.data.loc[self.data["duration"] != 0]["duration"].mean()
            minutes = seconds / 60
            minutes_left = int(minutes % 60)
            hours = minutes / 60
            hours_left = int(hours % 60)
            days = int(hours / 24)

        except:
            minutes_left = 0
            hours_left = 0
            days = 0

        #Buy and Sell count
        buy_count = self.data["buy_count"].sum()
        sell_count = self.data["sell_count"].sum()

        #Return over period
        return_over_period = self.data["cumulative_returns"].iloc[-1] * 100

        #Calcul drawdown max
        dd_max = -self.data["drawdown"].min() * 100

        #Hit ratio
        nb_trade_positive = len(self.data[self.data["returns"] > 0])
        nb_trade_negative = len(self.data[self.data["returns"] < 0])
        hit = nb_trade_positive * 100 / (nb_trade_positive + nb_trade_negative)

        #Risk reward ratio
        average_winning_value = self.data[self.data["returns"] > 0]["returns"].mean()
        average_losing_value = self.data[self.data["returns"] < 0]["returns"].mean()

        rr_ratio = -average_winning_value / average_losing_value

        #Metrics ret/month
        months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        years = ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"]

        #Computation monthly returns
        ben_month = []

        for month in months:
            for year in years:
                try:
                    information = self.data.loc[f"{year}-{month}"]
                    cum = information["returns"].sum()
                    ben_month.append(cum)
                except:
                    pass

        sr = pd.Series(ben_month, name="returns")

        pct_winning_month = (1-(len(sr[sr < 0]) / len(sr))) * 100
        best_month_return = np.max(ben_month) * 100
        worse_month_return = np.min(ben_month) * 100

        #Average monthly return
        cngr = np.mean(ben_month) * 100

        print("---------------------------------------------------------------------------------------------------------------")
        print(f"AVERAGE TRADE LIFTIME: {days}D {hours_left}H {minutes_left}M \t Nb BUY: {buy_count} \t Nb SELL: {sell_count}")
        print(f"Return period: {'%.2f' % return_over_period}% \t\t\t\t Drawdown max: {'%.2f' % dd_max}%")
        print(f"Hit ratio: {'%.2f' % hit}% \t\t\t\t\t\t Risk Reward Ratio: {'%.2f' % rr_ratio}")
        print(f"Best month return: {'%.2f' % best_month_return}% \t\t\t\t Worse month return: {'%.2f' % worse_month_return}%")
        print(f"Average monthly return: {'%.2f' % cngr}% \t\t\t\t\t Percentage profitable month: {'%.2f' % pct_winning_month}%")
        print("---------------------------------------------------------------------------------------------------------------")


    def get_ret_dd(self):
        self.get_vector_metrics()

        #Return over period
        return_over_period = self.data["cumulative_returns"].iloc[-1] * 100

        #Calcul drawdown max
        dd_max = self.data["drawdown"].min() * 100

        return return_over_period, dd_max
    
from ND_RsiSMA import *
df = pd.read_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_H4_READY.csv")

params = {
    "tp": 0.007,
    "sl": 0.003,
    "fast_sma": 50,
    "slow_sma": 200,
    "rsi_period": 14,
    "cost": 0.0001,
    "lever": 30,
}


BT = Backtest(df, RsiSma, params, run_directly=True,
              title="Walk-Forward optimization 2014 - 2024 EUR/USD H4")
