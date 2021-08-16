# Alma Project Aug

import pyRofex
from datetime import datetime, date, timedelta
import numpy as np
import yfinance as yf
import conector


def get_offer_price(message):
    try:
        offer_price = message["marketData"]["OF"][0]["price"]
    except IndexError:
        offer_price = None
    return offer_price


def get_bid_price(message):
    try:
        bid_price = message["marketData"]["BI"][0]["price"]
    except IndexError:
        bid_price = None
    return bid_price


def get_instrument(message):
    return message["instrumentId"]["symbol"]


def tasa_implicita(future_price, spot_price, time_to_maturity):
    if future_price is None or spot_price is None:
        return np.nan
    else:
        return (future_price / spot_price - 1) * 365 / time_to_maturity


def print_rates(rates):
    for key, value in rates.items():
        print("{}: {:.2%}".format(key, value), end=' ')


class Arbitraje:

    def __init__(self, dias_spot=2, spot_symbols=None, future_symbols=None):
        self.dias_spot = dias_spot
        self.spot_symbols = spot_symbols
        self.future_symbols = future_symbols
        self.instruments = self.spot_symbols + self.future_symbols  # se consolidan todos los intrumentos de Remarkets
        self.market_data = {key: {"bid_price": None, "offer_price": None} for key in self.instruments}  # se incia un diccionario que se va a ir actualizando con los precios BID y OFFER de la market data
        dlr_bid, dlr_ask = self.get_dolar_spot()  # se piden los precios bid y offer del spot de dolar
        self.market_data["DLR"] = {"bid_price": dlr_bid, "offer_price": dlr_ask}  # se agrega el spot de dolar al diccionario de la market data
        self.spot_symbols.append("DLR")
        self.colocadoras = {key: np.nan for key in self.future_symbols}  # se incian los diccionarios para las tasas colocadoras y tomadoras
        self.tomadoras = {key: np.nan for key in self.future_symbols}
        conector.init_login()  # se loguea con Remarkets
        self.time_to_maturity = {key: {} for key in self.future_symbols}  # se inicia un diccionario para almacenar los dias al vencimiento de cada futuro
        self.get_time_to_maturity()  # se calcula los dias al vencimiento para cada futuro
        conector.init_connection(self.instruments)  # se inicia la conexión con Remarkets para los instruments en self.instruments

    def get_dolar_spot(self):
        dolar_spot = yf.Ticker("ARS=X")
        return dolar_spot.info["bid"], dolar_spot.info["ask"]

    def run(self):
        pyRofex.add_websocket_market_data_handler(self.next)  # cada arribo nuevo de market data dispara el método self.next

    def next(self, message):
        print("Nueva MD")
        self.process_MD(message)
        self.process_rates()
        self.process_arbitrage()

    def process_MD(self, message):
        # Se extraen los precios del bid y offer de la nueva MD y se guardan en self.market_data
        try:
            instrument = get_instrument(message)
            bid_price = get_bid_price(message)
            offer_price = get_offer_price(message)
            self.market_data[instrument]["bid_price"] = bid_price
            self.market_data[instrument]["offer_price"] = offer_price
        except Exception as e:
            print("[process_MD] error {}".format(e))

    def get_time_to_maturity(self):
        # Se calculan los dias la vencimiento de los futuros. En el caso del dolar, se considera la liquidacion del spot como CI
        today = date.today()
        for item in self.time_to_maturity:
            expiry_date = pyRofex.get_instrument_details(item)["instrument"]["maturityDate"]
            time_to_maturity = datetime.strptime(expiry_date, '%Y%m%d').date() - today - timedelta(days=self.dias_spot)
            if "DLR" in item:
                time_to_maturity = time_to_maturity + timedelta(days=self.dias_spot)
            self.time_to_maturity[item] = time_to_maturity.days

    def process_rates(self):
        # Se calculan todas las tasas implicitas entre spots y futuros y se guardan en los diccionarios self.colocadoras y self.tomadoras
        for ticker in self.future_symbols:
            try:
                spot_symbol = self.get_spot_symbol(ticker)
                time_to_maturity = self.time_to_maturity[ticker]
                future_bid = self.market_data[ticker]["bid_price"]
                future_offer = self.market_data[ticker]["offer_price"]
                spot_bid = self.market_data[spot_symbol]["bid_price"]
                spot_offer = self.market_data[spot_symbol]["offer_price"]
                self.colocadoras[ticker] = tasa_implicita(future_bid, spot_offer, time_to_maturity)
                self.tomadoras[ticker] = tasa_implicita(future_offer, spot_bid, time_to_maturity)
            except Exception as e:
                print("[process_rates] error en ticker {}: {}".format(ticker, e))
        print("Tasas colocadoras:", end=" ")
        print_rates(self.colocadoras)
        print("\nTasas tomadoras:", end=" ")
        print_rates(self.tomadoras)
        print("")

    def get_spot_symbol(self, ticker):
        # Devuelve el spot a partir del ticker del futuro
        spot = ticker.split("/")[0]
        values = [k for k in self.spot_symbols if spot in k]
        if values:
            return values[0]
        else:
            raise Exception('Spot {} no se encuentra'.format(spot))

    def process_arbitrage(self):
        # Se buscan arbitrajes tal que la tasa colocadora sea mayor a la tasa tomadora y se printea la que tenga máximo spread
        max_colocadora_value, max_colocadora_key = self.find_max_rate()
        min_tomadora_value, min_tomadora_key = self.find_min_rate()
        if max_colocadora_value > min_tomadora_value:
            print("Hay un arbitraje colocando en {} con tasa {:.2%} y tomando en {} con tasa {:.2%}".format(max_colocadora_key, max_colocadora_value, min_tomadora_key, min_tomadora_value))
            print("")

    def find_max_rate(self):
        # Devuelve la tasa y el instrumento que tenga la mayor tasa de las colocadoras
        colocadora_values = [v for v in self.colocadoras.values() if v is not np.nan]
        if not colocadora_values:
            return np.nan, np.nan
        max_colocadora_value = max(colocadora_values)
        max_colocadora_key = [k for k, v in self.colocadoras.items() if v == max_colocadora_value]
        return max_colocadora_value, max_colocadora_key

    def find_min_rate(self):
        # Devuelve la tasa y el instrumento que tenga la menor tasa de las tomadoras
        tomadora_values = [v for v in self.tomadoras.values() if v is not np.nan]
        if not tomadora_values:
            return np.nan, np.nan
        min_tomadora_value = min(tomadora_values)
        min_tomadora_key = [k for k, v in self.tomadoras.items() if v == min_tomadora_value]
        return min_tomadora_value, min_tomadora_key
