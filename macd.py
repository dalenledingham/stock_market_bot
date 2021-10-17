import yfinance as yf
import numpy as np


def create_dataframe(ticker):
  """Get datafram from Yahoo Finance"""
  df = yf.Ticker(ticker).history(period='1y')[['Open','High','Low','Close','Volume']]

  ema_12 = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
  ema_26 = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
  macd = ema_12 - ema_26
  signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
  histogram = macd - signal

  df['MACD'] = df.index.map(macd)
  df['Signal'] = df.index.map(signal)
  df['Histogram'] = df.index.map(histogram)

  return df


def backtest():
  """Backtest against historical data"""

  for h in df['Histogram']:
    if h == np.nan:
      continue
    elif h > 0:
      # fake_buy()
      pass
    elif h < 0:
      # fake_sell()
      pass


if __name__ == '__main__':
  df = create_dataframe('AAPL')
  print(df)