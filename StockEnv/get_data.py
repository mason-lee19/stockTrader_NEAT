from sqlalchemy import create_engine,text
import pandas as pd
import yfinance as yf

class SqlDatabase:
    def __init__(self,table_name:str):
        self.table_name = table_name
        self.connection_string = 'sqlite:///StockEnv/db/neat_stock_data.db'

    def create_connection(self):
        self.engine = create_engine(self.connection_string)

    def pull_stock_data_yf(self,ticker:str,start_date:str='2020-01-01'):
        df = pd.DataFrame(yf.download(ticker, start=start_date))
        df['ticker'] = ticker
        df.drop(columns=['Adj Close'], inplace=True)
        df.reset_index(inplace=True)

        return df

    def push_to_db(self,df:pd.DataFrame):
        df.to_sql(self.table_name, con=self.engine, if_exists='replace', index=False)

    def query_ticker(self,ticker:str):
        try:
            query = f"SELECT * FROM {self.table_name} WHERE ticker = '{ticker}'"
            return pd.read_sql(query,self.engine)
        except:
            print(f'Could not find query for ticker: {ticker}')
            return pd.DataFrame()

    def query_date_range(self,ticker:str,date_start:str,date_end:str):
        pass

    def delete_stock_data(self,ticker:str):
        try:
            condition = f"ticker='{ticker}'"
            with self.engine.connect() as connection:
                result = connection.execute(text(f"DELETE FROM {self.table_name} WHERE {condition}"))
                connection.commit()

                print(f"Deleted {result.rowcount} rows(s) from {self.table_name}")
            
            connection.close()
        
        except:
            print(f"Connection to {self.table_name} failed or {ticker} does not exist in db")


