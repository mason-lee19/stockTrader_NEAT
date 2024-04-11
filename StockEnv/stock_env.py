from DataBase import DatabaseConfig, StockDataHandler, ResultsDataHandler

class StockEnv:
    def __init__(self):
        # Initialize database connections
        stock_db_config = DatabaseConfig(table_name='stock_data', url='sqlite:///DataBase/db/neat_stock_data.db')
        #results_db_config = DatabaseConfig(table_name='results',url='')

        self.stock_db_connection = StockDataHandler(stock_db_config)
        #self.results_db_connection = ResultsDatahandler(results_db_config)

        self.stocks = ['BTC-USD']

        # Initialize run values
        self.profit = 0

    def run(self):
        df = self.stock_db_connection.query_ticker('BTC-USD')
        print(df)