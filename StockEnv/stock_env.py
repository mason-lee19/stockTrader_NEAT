from DataBase import DatabaseConfig, StockDataHandler, ResultsDataHandler
import pandas as pd
from typing import List
import random

class StockEnv:
    def __init__(self,stock_list:List[str],trade_amount:int=1000,runs_per_stock:int=20,pre_trade_days:int=30,trading_days:int=90):
        # Initialize database connections
        stock_db_config = DatabaseConfig(table_name='stock_data', url='sqlite:///DataBase/db/neat_stock_data.db')
        results_db_config = DatabaseConfig(table_name='results',url='sqlite:///DataBase/db/result_data.db')

        self.stock_db_connection = StockDataHandler(stock_db_config)
        self.results_db_connection = ResultsDataHandler(results_db_config)

        self.stocks = stock_list

        # Initialize run values
        self.trade_amount = trade_amount
        self.runs_per_stock = runs_per_stock
        self.pre_trade_days = pre_trade_days
        self.trading_days = trading_days

        self.profit_percentage = 0
        self.buy_index = -1
        self.buy_signal = False

        self.results = {'stock':[],
                        'generation':[],
                        'genome_num':[],
                        'profit%':[],
                        'buy_price':[],
                        'sell_price':[]}

    def trade_loop(self,net,generation,genome_num):
        # Set run variables to their start values
        self.intialize_run_vars()

        # Loop for each stock
        for stock_ticker in self.stocks:
            df = self.stock_db_connection.query_ticker(stock_ticker)

            # Loop runs per stock
            for run_num in range(self.runs_per_stock):
                # Pull random start index integer eg randint(30,len(df)-120) for a 30 pre window and 90 day trading window
                # Subtract 252 to use the last year worth of data as validation
                start_index = random.randint(self.pre_trade_days,len(df)-
                                            (self.pre_trade_days+self.trading_days)-252)

                stock_slice = df.iloc[start_index:start_index+
                                      self.pre_trade_days+self.trading_days].copy()

                stock_slice.drop(columns=['ticker'],inplace=True)
                stock_slice.dropna(inplace=True)

                # column_names = stock_slice.columns.tolist()
                
                normalized_stock_slice = stock_slice.apply(self.normalize_data)
                normalized_stock_slice.dropna(inplace=True)
                # Reseting index allows utilization of ['index'] column to pull stock info from main df
                normalized_stock_slice.reset_index(inplace=True)

                # Loop through sliced and normalized data frame
                for idx in range(len(normalized_stock_slice)):
                    inputs = (self.buy_signal,
                              normalized_stock_slice['Open'].iloc[idx],
                              normalized_stock_slice['High'].iloc[idx],
                              normalized_stock_slice['Low'].iloc[idx],
                              normalized_stock_slice['Close'].iloc[idx],
                              normalized_stock_slice['Volume'].iloc[idx],
                              normalized_stock_slice['SMA_20'].iloc[idx],
                              normalized_stock_slice['SMA_50'].iloc[idx],
                              normalized_stock_slice['EMA_20'].iloc[idx],
                              normalized_stock_slice['RSI_14'].iloc[idx],
                              normalized_stock_slice['MACD'].iloc[idx],
                              normalized_stock_slice['MACD_Signal'].iloc[idx],
                              normalized_stock_slice['BB_Upper'].iloc[idx],
                              normalized_stock_slice['BB_Middle'].iloc[idx],
                              normalized_stock_slice['BB_Lower'].iloc[idx],
                              normalized_stock_slice['ATR_14'].iloc[idx],
                              normalized_stock_slice['OBV'].iloc[idx],
                              normalized_stock_slice['ADL'].iloc[idx])

                    output = net.activate(inputs)
                    decision = output.index(max(output))

                    # BUY Signal
                    if decision == 0 and not self.buy_signal:
                        self.buy_signal = True
                        self.buy_index = idx
                    # SELL Signal
                    elif decision == 1 and self.buy_signal:

                        buy_price = df['Close'].iloc[normalized_stock_slice['index'].iloc[self.buy_index]]
                        sell_price = df['Close'].iloc[normalized_stock_slice['index'].iloc[idx]]

                        profit_percent = self.calculate_profit_percentage(buy_price,sell_price)
                        self.profit_percentage += profit_percent*100

                        self.results['stock'].append(stock_ticker)
                        self.results['generation'].append(generation)
                        self.results['genome_num'].append(genome_num)
                        self.results['profit%'].append(self.profit_percentage)
                        self.results['buy_price'].append(buy_price)
                        self.results['sell_price'].append(sell_price)

                        self.buy_signal = False

                    # If == 2 than just wait

        
        # Push results to db
        self.results_db_connection.push_to_db(pd.DataFrame.from_dict(self.results))

        # Want to try and remove strategies that just don't make trades
        if self.profit_percentage == 0:
            return -10.0

        return self.profit_percentage

    def validation_loop(self,net):
        self.intialize_run_vars()

        for stock_ticker in self.stocks:

            df = self.stock_db_connection.query_ticker(stock_ticker)

            stock_slice = df.iloc[len(df)-252:len(df)].copy()

            stock_slice.drop(columns=['ticker'],inplace=True)
            stock_slice.dropna(inplace=True)

            # column_names = stock_slice.columns.tolist()
            
            normalized_stock_slice = stock_slice.apply(self.normalize_data)
            normalized_stock_slice.dropna(inplace=True)
            # Reseting index allows utilization of ['index'] column to pull stock info from main df
            normalized_stock_slice.reset_index(inplace=True)

            for idx in range(30,len(normalized_stock_slice)):
                inputs = (self.buy_signal,
                          normalized_stock_slice['Open'].iloc[idx],
                          normalized_stock_slice['High'].iloc[idx],
                          normalized_stock_slice['Low'].iloc[idx],
                          normalized_stock_slice['Close'].iloc[idx],
                          normalized_stock_slice['Volume'].iloc[idx],
                          normalized_stock_slice['SMA_20'].iloc[idx],
                          normalized_stock_slice['SMA_50'].iloc[idx],
                          normalized_stock_slice['EMA_20'].iloc[idx],
                          normalized_stock_slice['RSI_14'].iloc[idx],
                          normalized_stock_slice['MACD'].iloc[idx],
                          normalized_stock_slice['MACD_Signal'].iloc[idx],
                          normalized_stock_slice['BB_Upper'].iloc[idx],
                          normalized_stock_slice['BB_Middle'].iloc[idx],
                          normalized_stock_slice['BB_Lower'].iloc[idx],
                          normalized_stock_slice['ATR_14'].iloc[idx],
                          normalized_stock_slice['OBV'].iloc[idx],
                          normalized_stock_slice['ADL'].iloc[idx])

                output = net.activate(inputs)

                decision = output.index(max(output))

                if decision == 0 and not self.buy_signal:
                    buy_signal = True
                    self.buy_index = idx
                elif decision == 1 and self.buy_signal:
                    buy_signal = False

                    buy_price = df['Close'].iloc[normalized_stock_slice['index'].iloc[self.buy_index]]
                    sell_price = df['Close'].iloc[normalized_stock_slice['index'].iloc[idx]]

                    profit_percent = self.calculate_profit_percentage(buy_price,sell_price)
                    self.profit_percentage += profit_percent*100

        # Want to try and remove strategies that just don't make trades
        if self.profit_percentage == 0:
            return -10.0

        return self.profit_percentage

                    

    def intialize_run_vars(self):
        self.profit = 0
        self.buy_index = -1
        self.buy_signal = False
        self.sell_signal = False

    def normalize_data(self,col):
        rolling_max = col.rolling(window=90, min_periods=30).max()
        rolling_min = col.rolling(window=90, min_periods=30).min()

        normalized_col = (col - rolling_min) / (rolling_max-rolling_min)

        return normalized_col

    def calculate_profit_percentage(self,buy_price:int,sell_price:int):
        profit = sell_price - buy_price
        profit_percentage = (profit / buy_price)

        return profit_percentage