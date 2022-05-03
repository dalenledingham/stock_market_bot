import yfinance as yf
import datetime
import time
import main


api = main.api


def check_market_open():
    """Check if market is open, wait until open if closed"""
    clock = api.get_clock()

    if not clock.is_open:
        next_open = clock.next_open.timestamp()
        now = datetime.datetime.now().timestamp()
        seconds = next_open - now
        print("Market is closed\n")
        time.sleep(seconds)


def create_dataframe(symbol, period):
    """Get datafram from Yahoo Finance"""
    dataframe = yf.Ticker(symbol).history(period=period)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]

    ema_12 = dataframe["Close"].ewm(span=12, adjust=False, min_periods=12).mean()
    ema_26 = dataframe["Close"].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    histogram = macd - signal

    dataframe["MACD"] = dataframe.index.map(macd)
    dataframe["Signal"] = dataframe.index.map(signal)
    dataframe["Histogram"] = dataframe.index.map(histogram)

    return dataframe


def check_for_position(symbol):
    """Check if position for this symbol exists"""
    try:
        api.get_position(symbol)
        return True
    except:
        return False


def new_position_qty(equity, buying_power, last_price):
    """Determine shares quantity for new position"""
    order_qty = 0

    # if can afford more than one share
    if buying_power > last_price:

        # set order quantity to not exceed more than 5% of portfolio equity (5% rule)
        if buying_power > (equity * 0.1):
            order_qty = equity * 0.1 // last_price
            return order_qty
        else:
            order_qty = buying_power // last_price
            return order_qty

    # if cannot afford at least one share
    else:
        order_qty = 0
        return order_qty


def add_to_position_qty(equity, buying_power, last_price, position):
    """Determine shares quantity to add to existing position"""
    order_qty = 0

    # if can afford more than 1 share
    if buying_power > last_price:

        # set order quantity to not exceed more than 5% of portfolio equity (5% rule)
        # if can get at least one share while within 5% rule
        if ((equity * 0.1) - float(position.market_value)) // last_price > 0:
            order_qty = ((equity * 0.1) - float(position.market_value)) // last_price
            return order_qty
        else:
            order_qty = 0
            return order_qty

    # if cannot afford at least one share
    else:
        order_qty = 0
        return order_qty


def buy(symbol, qty):
    """Submit buy order"""
    api.submit_order(
        symbol=symbol,
        qty=qty,
        side="buy",
        type="market",
        time_in_force="day",
    )


def sell(symbol, qty):
    """Submit a sell order"""
    api.submit_order(
        symbol=symbol,
        qty=qty,
        side="sell",
        type="market",
        time_in_force="day",
    )


def print_portfolio(account, portfolio):
    """Print portfolio positions and equity"""
    print("\nPortfolio:")
    if portfolio:
        for position in portfolio:
            print(f"{position.symbol}")
            print(f"\tShares: {position.qty}")
            print(f"\tCurrent Price: {position.current_price}")
            print(f"\tAvg Entry Price: {position.avg_entry_price}")
            print(f"\tMarket Value: {position.market_value}")
            print(
                f"\tIntraday Gain/Loss: {position.unrealized_intraday_pl} ({position.unrealized_intraday_plpc}%)"
            )
            print(
                f"\tTotal Gain/Loss: {position.unrealized_pl} ({position.unrealized_plpc}%)"
            )
        print()
    else:
        print("No positions\n")

    print(f"Equity: {account.equity}")
    print(f"Today Gain/Loss: {float(account.equity) - float(account.last_equity)}\n")


def run(symbols, period):
    """Run algorithm on live market"""
    while True:
        check_market_open()

        account = api.get_account()

        for symbol in symbols:
            dataframe = create_dataframe(symbol, period)
            print(f'{symbol}: {dataframe["Histogram"][-1]}')
            last_price = dataframe["Close"][-1]

            # if open position for this symbol exists
            if check_for_position(symbol):
                position = api.get_position(symbol)

                # if buy signal
                if dataframe["Histogram"][-1] > 0:
                    equity = float(account.equity)
                    buying_power = float(account.buying_power)
                    qty = add_to_position_qty(
                        equity, buying_power, last_price, position
                    )
                    if qty > 0:
                        buy(symbol, qty)
                        print(f"\tBUY {qty} shares of {symbol} for ${last_price * qty}")

                # if sell signal
                elif dataframe["Histogram"][-1] < 0:
                    qty = position.qty
                    sell(symbol, qty)
                    print(
                        f"\tSELL {qty} shares of {symbol} for ${position.market_value}"
                    )

            # if no position for this symbol exists
            else:
                if dataframe["Histogram"][-1] > 0:
                    equity = float(account.equity)
                    buying_power = float(account.buying_power)
                    qty = new_position_qty(equity, buying_power, last_price)
                    if qty > 0:
                        buy(symbol, qty)
                        print(f"\tBUY {qty} shares of {symbol} for ${last_price * qty}")

        portfolio = api.list_positions()
        print_portfolio(account, portfolio)

        time.sleep(60)
