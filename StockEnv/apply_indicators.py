import talib as ta
import pandas as pd

class ApplyIndicators:

    def apply_ta(self,df:pd.DataFrame):
        df = self.apply_indicators(df)
        return df

    def apply_indicators(self,df:pd.DataFrame):
        self.indicators = Indicators(df)

        ### Apply Techincal Indicators to dataframe ###

        # Simple moving average
        self.indicators.sma_n(20)
        self.indicators.sma_n(50)

        # Exponential Moving Average
        self.indicators.ema_n(20)
        self.indicators.ema_n(50)

        # Relative Strength Index
        self.indicators.rsi_n(14)

        # Moving Average Convergence Divergence
        self.indicators.macd()

        # Bollinger Bands
        self.indicators.bbands()

        # Average True Range
        self.indicators.atr_n(14)

        # On-Balance Volume
        self.indicators.obv()

        # Accumulation/Distribution Line
        self.indicators.adl()

        ### -------------------------------------- ###

        return self.indicators.df
        

class Indicators():
    def __init__(self,df:pd.DataFrame):
        self.df = df

    def sma_n(self,time_period:int=20):
        column_name = 'SMA_' + str(time_period)
        self.df[column_name] = ta.SMA(self.df['Close'], timeperiod=time_period)
    
    def ema_n(self,time_period:int=20):
        column_name = 'EMA_' + str(time_period)
        self.df[column_name] = ta.EMA(self.df['Close'], timeperiod=time_period)

    def rsi_n(self,time_period:int=14):
        column_name = 'RSI_' + str(time_period)
        self.df[column_name] = ta.RSI(self.df['Close'], timeperiod=time_period)

    def macd(self):
        macd, signal, _ = ta.MACD(self.df['Close'])
        self.df['MACD'] = macd
        self.df['MACD_Signal'] = signal

    def bbands(self):
        upper, middle, lower = ta.BBANDS(self.df['Close'])
        self.df['BB_Upper'] = upper
        self.df['BB_Middle'] = middle
        self.df['BB_Lower'] = lower

    def stoch_osci(self):
        slowk, slowd = ta.STOCH(self.df['High'],self.df['Low'], self.df['Close'])
        self.df['Stoch_Oscil_K'] = slowk
        self.df['Stoch_Oscil_D'] = slowd

    def atr_n(self,time_period:int=14):
        column_name = 'ATR_' + str(time_period)
        self.df[column_name] = ta.ATR(self.df['High'], self.df['Low'], self.df['Close'], timeperiod=time_period)

    def obv(self):
        self.df['OBV'] = ta.OBV(self.df['Close'], self.df['Volume'])

    def adl(self):
        self.df['ADL'] = ta.AD(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])

    def vwap(self):
        self.df['VWAP'] = ta.VWAP(self.df['High'], self.df['Low'], self.df['Close'], self.df['Volume'])

    def eom_n(self,time_period:int=14):
        column_name = 'EOM_' + str(time_period)
        self.df[column_name] = ta.EOM(self.df['High'], self.df['Low'], self.df['Volume'], timeperiod=time_period)
    

    

