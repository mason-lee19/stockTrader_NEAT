from StockEnv import SqlDatabase, ApplyIndicators

def main():
    table_name = 'stock_data'

    sql = SqlDatabase(table_name)
    sql.create_connection()

    df = sql.query_ticker('BTC-USD')
    if len(df) == 0:
        df = sql.pull_stock_data_yf('BTC-USD')
        ta = ApplyIndicators()
        df = ta.apply_ta(df)
        sql.push_to_db(df)
        
    print(df)

    # Add all technical indicators
    # sql.push_to_db('BTC-USD')
    # df = sql.pull_stock_data_sql('BTC-USD')


if __name__ == '__main__':
    main()