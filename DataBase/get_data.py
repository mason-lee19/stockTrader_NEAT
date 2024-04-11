from Indicators import ApplyIndicators

from sqlalchemy import create_engine,text
import pandas as pd
import yfinance as yf


class DatabaseConfig:
    def __init__(self,table_name:str,url:str):
        self.table_name = table_name
        self.url = url

class StockDataHandler:
    def __init__(self,config):
        self.engine = create_engine(config.url)
        self.table_name = config.table_name

    def pull_stock_data_yf(self,ticker:str,start_date:str='2020-01-01'):
        df = pd.DataFrame(yf.download(ticker, start=start_date))
        df['ticker'] = ticker
        df.drop(columns=['Adj Close'], inplace=True)

        return df

    def push_to_db(self,df:pd.DataFrame):
        df.to_sql(self.table_name, con=self.engine, if_exists='replace', index=False)

    def query_ticker(self,ticker:str):
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ticker = '{ticker}'"
            print(f'Found {ticker} in {self.table_name}')
            return pd.read_sql(query,self.engine)
        except:
            print(f'Could not find query for ticker: {ticker}')
            print(f'Attempting to download data for: {ticker}')
            df = self.pull_stock_data_yf(ticker)
            df = ApplyIndicators().apply_ta(df)
            df.dropna(inplace=True)
            self.push_to_db(df)
            print(f'Retrying query for ticker: {ticker}')

            try:
                query = f"SELECT * FROM {self.table_name} WHERE ticker = '{ticker}'"
                return pd.read_sql(query,self.engine)
            except:
                print(f'Retry Failed for ticker: {ticker}')
                return pd.DataFrame()
    
    def query_date_range(self,ticker:str,date_start:str,date_end:str):
        pass

    def delete_data(self,ticker:str):
        try:
            condition = f"ticker='{ticker}'"
            with self.engine.connect() as connection:
                result = connection.execute(text(f"DELETE FROM {self.table_name} WHERE {condition}"))
                connection.commit()

                print(f"Deleted {result.rowcount} rows(s) from {self.table_name}")
            
            connection.close()

            return True
        
        except:
            print(f"Connection to {self.table_name} failed or {ticker} does not exist in db")

            return False

class ResultsDataHandler:
    def __init__(self,config):
        self.engine = create_engine(config.url)
        self.table_name = config.table_name

