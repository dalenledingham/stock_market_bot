import alpaca_trade_api as tradeapi
import yfinance as yf
import datetime
import time
import graph
import keys
import macd_backtest


# Alpaca API connection
APCA_API_KEY_ID = keys.key_id
APCA_API_SECRET_KEY = keys.secret_key
APCA_API_BASE_URL = keys.base_url
api = tradeapi.REST(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL)


def check_market_open():
  """Check if market is open, wait until open if closed"""
  clock = api.get_clock()

  if not clock.is_open:
    next_open = clock.next_open.timestamp()
    now = datetime.datetime.now().timestamp()
    seconds = next_open - now
    print('Market is closed\n')
    time.sleep(seconds)


def create_dataframe(symbol, period):
  """Get datafram from Yahoo Finance"""
  df = yf.Ticker(symbol).history(period=period)[['Open','High','Low','Close','Volume']]

  ema_12 = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
  ema_26 = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
  macd = ema_12 - ema_26
  signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
  histogram = macd - signal

  df['MACD'] = df.index.map(macd)
  df['Signal'] = df.index.map(signal)
  df['Histogram'] = df.index.map(histogram)

  return df


def run(symbol, period):
  """Run algorithm on live market"""
  while True:
    check_market_open()

    account = api.get_account()
    portfolio = api.list_positions()
    open_orders = api.list_orders(status='open')

    df = create_dataframe(symbol, period)
    last_price = df['Close'][-1]

    if float(account.buying_power) > last_price:
      qty = float(account.buying_power) // last_price
    else: qty = 0

    if not portfolio and not open_orders and df['Histogram'][-1] > 0:
      if qty > 0:
        buy(symbol, qty)
        trailing_stop_sell(symbol, qty)
        print('BUY')
    elif portfolio and df['Histogram'][-1] < 0:
      qty = portfolio[-1].qty
      sell(symbol, qty)
      print('SELL')

    print('Portfolio:')
    if portfolio: 
      for position in portfolio:
        print(f'{position.symbol}')
        print(f'\tShares: {position.qty}')
        print(f'\tCurrent Price: {position.current_price}')
        print(f'\tAvg Entry Price: {position.avg_entry_price}')
        print(f'\tMarket Value: {position.market_value}')
        print(f'\tToday Gain/Loss: {position.unrealized_intraday_pl} ({position.unrealized_intraday_plpc})')
        print(f'\tTotal Gain/Loss: {position.unrealized_pl} ({position.unrealized_plpc})')
      print()
    else: print('No positions\n')

    time.sleep(60)


def buy(symbol, qty):
  """Submit buy order"""
  api.submit_order(
    symbol = symbol,
    qty = qty,
    side = buy,
    type = 'market',
    time_in_force = 'day',
  )

def trailing_stop_sell(symbol, qty):
  """Submit a sell order with a traling stop of 2%"""
  api.submit_order(
    symbol = symbol,
    qty = qty,
    side = sell,
    type = 'trailing_stop',
    trail_percent = 2.0,
    time_in_force = 'day',
  )

def sell(symbol, qty):
  """Submit a sell order"""
  api.submit_order(
    symbol = symbol,
    qty = qty,
    side = buy,
    type = 'market',
    time_in_force = 'day',
  )


if __name__ == '__main__':
  symbol = 'AAPL'
  run(symbol, '3mo')

  # # Backtest against historical data
  # df = create_dataframe(symbol, '1y')
  # print(df)
  # macd_backtest.backtest(df)

  # # Plot dataframe, opens in browser
  # graph.plot_data(symbol, df)