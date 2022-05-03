# Alpaca Trading Bot

## **I am not a financial advisor. This is not financial advice.**

This repository contains the the code for my stock trading bot using the Alpaca Trade API.

The implemented strategy is an analysis of a stock's MACD (Moving Average Convergence Divergence) to determine buy/sell signals.

To use this bot, first clone this repository. Then create an account on Alpaca and generate your API keys. Put those keys in a new file called _keys.py_ in the same directory with the following naming conventions:

```
key_id = '<YOUR_KEY_ID>'
secret_key = '<YOUR_SECRET_KEY>'
base_url = 'https://paper-api.alpaca.markets' # use this url for paper trading
```

Check the [requirements.txt](/requirements.txt) file and install all required libraries using `pip3 install -r requirements.txt`

Then you can run the program using the command `python3 main.py`

The program will run infinitely, so to stop it you must execute a keyboard interrupt (CTRL+C on Windows, ^C on MacOS).

If you wish to backtest the program agains historical data rather than run it live, comment out or delete the `run()` function call and uncomment the following code block:

```
# Backtest against historical data
for position in positions:
    account = macd_backtest.Account()
    dataframe = macd.create_dataframe(position.symbol, "1y")
    print(dataframe)
    macd_backtest.backtest(account, position, dataframe)
```

Run the program again to backtest the algorithm.

To plot graphs using plotly, uncomment this line:

```
macd_graph.plot_data(position.symbol, dataframe)
```
