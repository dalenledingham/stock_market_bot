import alpaca_trade_api as tradeapi
import keys
from macd import macd, macd_backtest, macd_graph


# Alpaca API connection
APCA_API_KEY_ID = keys.key_id
APCA_API_SECRET_KEY = keys.secret_key
APCA_API_BASE_URL = keys.base_url
api = tradeapi.REST(
    key_id=APCA_API_KEY_ID,
    secret_key=APCA_API_SECRET_KEY,
    base_url=APCA_API_BASE_URL,
)


if __name__ == "__main__":
    AAPL = macd_backtest.Position("AAPL")
    KO = macd_backtest.Position("KO")
    SPY = macd_backtest.Position("SPY")
    TSLA = macd_backtest.Position("TSLA")
    positions = [AAPL, KO, SPY, TSLA]
    symbols = [position.symbol for position in positions]

    # Run in live market
    macd.run(symbols, "3mo")

    # Backtest against historical data
    # for position in positions:
    #     account = macd_backtest.Account()
    #     dataframe = macd.create_dataframe(position.ticker, "1y")
    #     print(dataframe)
    #     macd_backtest.backtest(account, position, dataframe)

    #     # Plot dataframe, opens in browser
    #     macd_graph.plot_data(position.ticker, dataframe)
