import yfinance as yf
import numpy as np


# Balance variables for backtesting
start_balance = 100000
balance = start_balance

# Quantity and position variables
qty = 0
position_qty = 0
position_held = False
count = 0

# First buy variables
first_buy = True
first_price = 0
first_qty = 0


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


def backtest(df):
  """Backtest against historical data"""
  global count

  for h in df['Histogram']:
    if h == np.nan:
      count += 1
      continue
    elif h > 0 and not position_held:
      fake_buy(df)
    elif h < 0 and position_held:
      fake_sell(df)
    else:
      count += 1


def fake_buy(df):
  """Buy function for backtesting"""
  global balance
  global qty
  global position_qty
  global position_held
  global first_buy
  global first_price
  global first_qty
  global count

  last_price = df['Close'][count]

  qty = balance // last_price

  if first_buy:
    first_buy = False
    first_price = last_price
    first_qty = qty

  if qty > 0:
    balance -= last_price * qty
    position_held = True
    position_qty = qty

  count += 1


def fake_sell(df):
  """Sell function for backtesting"""
  global balance
  global qty
  global position_held
  global count

  last_price = df['Close'][count]

  balance += last_price * qty
  position_held = False
  qty = 0
  
  count += 1


if __name__ == '__main__':
  df = create_dataframe('AAPL')
  print(df)

  backtest(df)

  # Print algorithm results
  if position_held:
    print('Balance from algorithm: ' + str(balance + df['Close'][-1] * qty))
  else:
    print('Balance from algorithm: ' + str(balance))

  # Print results if held at first buy
  print('Balance if held: ' + str(start_balance + (df['Close'][-1] * first_qty) - (first_price * first_qty)))
  