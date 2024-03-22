from data_pre_processing import sma, rsi
import pandas as pd




params = {
    "fast_sma": 30,
    "slow_sma": 120,
    "rsi": 14,
    "tp": 0.005,
    "sl": 0.003,
    "cost": 0.0001,
    "leverage": 30,
}



class RsiSma:
    def __init__(self, data, parameters):
        self.data = data
        self.fast_sma = parameters["fast_sma"]
        self.slow_sma = parameters["slow_sma"]
        self.rsi = parameters["rsi"]
        self.tp = parameters["tp"]
        self.sl = parameters["sl"]
        self.cost = parameters["cost"]
        self.leverage = parameters["leverage"]
        self.start_date_backtest = self.data.index[0]


        #Get Entry parameters
        self.buy = False
        self.sell = False
        self.open_buy_price = None
        self.open_sell_price = None
        self.entry_time = None
        self.exit_time = None

        #Get Exit parameters
        self.var_buy_high = None
        self.var_sell_high = None
        self.var_buy_low = None
        self.var_sell_low = None


        pass

    def get_features(self):
        #Create new features
        self.data = sma(self.data, "close", self.fast_sma)
        self.data = sma(self.data, "close", self.slow_sma)
        self.data = rsi(self.data, "close", self.rsi)

        #Def signals
        self.data["signal"] = 0
        self.data["RSI_divergence"] = self.data["RSI"].shift(1)

        condition_1_buy = self.data[f"SMA_{self.fast_sma}"] < self.data[f"SMA_{self.slow_sma}"] 
        condition_1_sell = self.data[f"SMA_{self.fast_sma}"] > self.data[f"SMA_{self.slow_sma}"]

        condition_2_buy = self.data[f"RSI"] > self.data["RSI_divergence"]
        condition_2_sell = self.data[f"RSI"] < self.data["RSI_divergence"]

        self.data.loc[condition_1_buy & condition_2_buy, "signal"] = 1
        self.data.loc[condition_1_sell & condition_2_sell, "signal"] = -1

        return self.data
    
    def get_entry_signal(self, time):
        #If we are in first row, we can't get the signal
        if len(self.data.loc[:time]) < 2:
            return 0, self.entry_time


        entry_signal = 0
        if self.data.loc[:time]["signal"][-2] == 1:
            entry_signal = 1
        elif self.data.loc[:time]["signal"][-2] == -1:
            entry_signal = -1

        #Enter in buy position only if we want to, and we aren't already in a buy position
        if entry_signal == 1 and not self.buy and not self.sell:
            self.buy = True
            self.open_buy_price = self.data.loc[time]["open"]
            self.entry_time = time

        #Enter in sell position only if we want to, and we aren't already in a sell position
        elif entry_signal == -1 and not self.buy and not self.sell:
            self.sell = True
            self.open_sell_price = self.data.loc[time]["open"]
            self.entry_time = time

        return entry_signal, self.entry_time
    
    def get_exit_signal(self, time):
        #If we are in first row, we can't get the signal
        if self.buy:
            self.var_buy_high = (self.data.loc[time]["high"] - self.open_buy_price) / self.open_buy_price
            self.var_buy_low = (self.data.loc[time]["low"] - self.open_buy_price) / self.open_buy_price

            #Checking if at least one of the thresholds is reached
            if (self.tp < self.var_buy_high and (self.var_buy_low < self.sl)):
                
                #Close with a positive PnL if high_time is before low_time
                if self.data.loc[time]["high_time"] < self.data.loc[time]["low_time"]:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = (self.tp - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_buy, self.exit_time
                
                #Close with a negative PnL if low_time is before high_time
                elif self.data.loc[time]["low_time"] < self.data.loc[time]["high_time"]:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = (self.sl - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_buy, self.exit_time
                
                else:
                    self.buy = False
                    self.open_buy_price = None
                    position_return_buy = 0
                    self.exit_time = time
                    return position_return_buy, self.exit_time
                
            elif self.tp < self.var_buy_high:
                self.buy = False
                self.open_buy_price = None
                position_return_buy = (self.tp - self.cost) * self.leverage
                self.exit_time = time
                return position_return_buy, self.exit_time
            
            #Close with a negative PnL if low_time is before high_time
            elif self.var_buy_low < self.sl:
                self.buy = False
                self.open_buy_price = None
                position_return_buy = (self.sl - self.cost) * self.leverage
                self.exit_time = time
                return position_return_buy, self.exit_time
            
        #Verify if we need to close a position and update the variants if we are in sell position
            
            if self.sell:
                self.var_sell_high = -(self.data.loc[time]["high"] - self.open_sell_price) / self.open_sell_price
                self.var_sell_low = -(self.data.loc[time]["low"] - self.open_sell_price) / self.open_sell_price

                #Checking if at least one of the thresholds is reached
                if (self.tp < self.var_sell_high and (self.var_sell_low < self.sl)):

                    #Close with a positive PnL if high_time is before low_time
                    if self.data.loc[time]["low_time"] < self.data.loc[time]["high_time"]:
                        self.sell = False
                        self.open_sell_price = None
                        position_return_sell = (self.tp - self.cost) * self.leverage
                        self.exit_time = time
                        return position_return_sell, self.exit_time

                    #Close with a negative PnL if low_time is before high_time
                    elif self.data.loc[time]["high_time"] < self.data.loc[time]["low_time"]:
                        self.sell = False
                        self.open_sell_price = None
                        position_return_sell = (self.sl - self.cost) * self.leverage
                        self.exit_time = time
                        return position_return_sell, self.exit_time

                    else:
                        self.sell = False
                        self.open_sell_price = None
                        position_return_sell = 0
                        self.exit_time = time
                        return position_return_sell, self.exit_time

                elif self.tp < self.var_sell_high:
                    self.sell = False
                    self.open_sell_price = None
                    position_return_sell = (self.tp - self.cost) * self.leverage
                    self.exit_time = time
                    return position_return_sell, self.exit_time
                
        return 0, None
            
df = pd.read_csv(r"C:\Users\nikol\algo\oanda_algo_trading\data\EUR_USD_H4_READY.csv", index_col="time", parse_dates=True)

STRATEGY = RsiSma(df, params)
STRATEGY.get_features()

for time in df.index:
    open_price, entry_time = STRATEGY.get_entry_signal(time)
    print("OPEN", open_price, entry_time)

    returns, exit_time = STRATEGY.get_exit_signal(time)
    print("CLOSE", returns, exit_time)