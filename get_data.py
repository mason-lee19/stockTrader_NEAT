from sqlalchemy import create_engine,text
import pandas as pd
import yfinance as yf

class SqlDatabase:
    def __init__(self):
        self.table_name = 'stock_data'
        self.connection_string = 'sqlite:///neat_stock_data.db'

    def create_connection(self):
        self.engine = create_engine(self.connection_string)

    def pull_stock_data_yf(self,ticker:str,start_date:str='2020-01-01'):
        data = yf.download(ticker, start=start_date)
        return data

    def add_stock_data(self,ticker:str):
        df = pd.DataFrame(self.pull_stock_data_yf(ticker))
        df['ticker'] = ticker
        df.drop(['High','Low','Close'])
        df.to_sql(self.table_name, con=self.engine, if_exists='replace', index=False)

    def pull_stock_data_sql(self,ticker:str):
        try:
            condition = f"ticker = '{ticker}'"
            query = f"SELECT * FROM {self.table_name} WHERE {condition}"

            return pd.read_sql(query,self.engine)
        except:
            print(f"{ticker} does not exist")
            
            return pd.DataFrame()

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
