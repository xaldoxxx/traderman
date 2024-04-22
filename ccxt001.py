import ccxt
print(ccxt.exchanges) # devuelve una lista de mercados que ccxt trabaja
exchanges = ccxt.binance() # creamos una instancia 
print(exchanges.fetchMarkets())
