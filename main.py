import alpaca_trade_api as tradeapi
import keys
from macd import macd, macd_backtest, macd_graph


# Alpaca API connection
APCA_API_KEY_ID = keys.key_id
APCA_API_SECRET_KEY = keys.secret_key
APCA_API_BASE_URL = keys.base_url
api = tradeapi.REST(
    key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL
)


if __name__ == "__main__":
    symbols = ["AAPL"]
    #   macd.run(symbols, '3mo')

    # # Backtest against historical data
    for symbol in symbols:
        df = macd.create_dataframe(symbol, "1y")
        print(df)
        macd_backtest.backtest(df)
        # # Plot dataframe, opens in browser
        # macd_graph.plot_data(symbol, df)
