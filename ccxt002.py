import ccxt
import pandas as pd

print(ccxt.exchanges) # devuelve una lista de mercados que ccxt trabaja
exchange = ccxt.binance() # creamos una instancia
markets = exchange.fetchMarkets()
markets_df = pd.DataFrame(markets)
print(markets_df)
