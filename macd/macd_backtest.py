import numpy


class Account:
    def __init__(self, balance=100000, start_balance=100000, positions=[]):
        self.balance = balance
        self.start_balance = start_balance
        self.positions = positions


class Position:
    def __init__(
        self,
        ticker,
        position_held=False,
        position_qty=0,
        first_buy=True,
        first_price=0,
        first_qty=0,
    ):
        self.ticker = ticker
        self.position_held = position_held
        self.position_qty = position_qty
        self.first_buy = first_buy
        self.first_price = first_price
        self.first_qty = first_qty
        self.count = 0
        self.purchase_qty = 0


def backtest(account, position, dataframe):
    """Backtest against historical data"""
    for histogram in dataframe["Histogram"]:
        if histogram == numpy.nan:
            position.count += 1
            continue
        elif histogram > 0 and not position.position_held:
            fake_buy(account, position, dataframe)
        elif histogram < 0 and position.position_held:
            fake_sell(account, position, dataframe)
        else:
            position.count += 1

    # Update final balance
    if position.position_held:
        account.balance += dataframe["Close"][-1] * position.purchase_qty

    # Print algorithm results
    print("Balance from algorithm: " + str(account.balance))

    # Print results if held at first buy
    print(
        "Balance if held: "
        + str(
            account.start_balance
            + (dataframe["Close"][-1] * position.first_qty)
            - (position.first_price * position.first_qty)
        )
    )


def fake_buy(account, position, dataframe):
    """Buy function for backtesting"""
    last_price = dataframe["Close"][position.count]

    position.purchase_qty = account.balance // last_price

    if position.first_buy:
        position.first_buy = False
        position.first_price = last_price
        position.first_qty = position.purchase_qty

    if position.purchase_qty > 0:
        account.balance -= last_price * position.purchase_qty
        position.position_held = True
        position.position_qty = position.purchase_qty

    position.count += 1


def fake_sell(account, position, dataframe):
    """Sell function for backtesting"""
    last_price = dataframe["Close"][position.count]

    account.balance += last_price * position.purchase_qty
    position.position_held = False
    position.position_qty = 0

    position.count += 1
