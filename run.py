from arbitraje import Arbitraje


dias_spot = 2  # Dias para la liquidacion del spot de las acciones

spot_symbols = ["MERV - XMEV - GGAL - 48hs",
                "MERV - XMEV - PAMP - 48hs",
                "MERV - XMEV - YPFD - 48hs"]

future_symbols = ["GGAL/AGO21",
                  "PAMP/AGO21",
                  "YPFD/AGO21",
                  "DLR/AGO21",
                  "DLR/SEP21"]

if __name__ == '__main__':
    A = Arbitraje(dias_spot, spot_symbols, future_symbols)
    A.run()
