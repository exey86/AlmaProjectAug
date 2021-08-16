import pyRofex


def init_login(user="exey865104", password="wqdnfX3&", account="REM5104"):
    # Set the the parameter for the REMARKET environment
    pyRofex.initialize(user=user,
                       password=password,
                       account=account,
                       environment=pyRofex.Environment.REMARKET)


def init_connection(instruments):
    # First we define the handlers that will process the messages and exceptions.
    def market_data_handler(message):
        #print("Market Data Message Received: {0}".format(message))
        pass

    def order_report_handler(message):
        pass

    def error_handler(message):
        print("Error Message Received: {0}".format(message))

    def exception_handler(e):
        print("Exception Occurred: {0}".format(e.message))

    # Initiate Websocket Connection
    pyRofex.init_websocket_connection(market_data_handler=market_data_handler,
                                      order_report_handler=order_report_handler,
                                      error_handler=error_handler,
                                      exception_handler=exception_handler)

    # Uses the MarketDataEntry enum to define the entries we want to subscribe to
    entries = [pyRofex.MarketDataEntry.BIDS,
               pyRofex.MarketDataEntry.OFFERS]

    # Subscribes to receive market data messages **
    pyRofex.market_data_subscription(tickers=instruments,
                                     entries=entries)

    # Subscribes to receive order report messages (default account will be used) **
    pyRofex.order_report_subscription()
