# buscamos pparidad con el usdt

import ccxt
import pandas as pd

#print(ccxt.exchanges) # devuelve una lista de mercados que ccxt trabaja
exchange = ccxt.binance() # creamos una instancia
markets = exchange.fetchMarkets()
markets_df = pd.DataFrame(markets)
markets_usdt = markets_df[(markets_df['quote'].str.contains('USDT')) & (markets_df['spot'])] # busco solo pares usdt y que esten en spot o estan prendidos
markets_usdt.set_index('id', inplace=True)
print(markets_usdt)
