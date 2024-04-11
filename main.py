from StockEnv import stock_env
from DataBase import DatabaseConfig, StockDataHandler, ResultsDataHandler

def main():
    stock_db_config = DatabaseConfig(table_name='stock_data', url='sqlite:///DataBase/db/neat_stock_data.db')
    #results_db_config = DatabaseConfig(table_name='results',url='')

    stock_db_connection = StockDataHandler(stock_db_config)
    #results_db_connection = ResultsDataHandler(results_db_config)

    df = stock_db_connection.query_ticker('BTC-USD')

    print(df)
    

if __name__ == '__main__':
    main()