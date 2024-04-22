import ccxt
import pandas as pd
import numpy as np

# Crear una instancia del exchange Binance
exchange = ccxt.binance()

# Obtener los datos del par de trading BTC/USDT
btc_usdt_data = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h')

# Convertir los datos en un DataFrame de pandas
btc_usdt_df = pd.DataFrame(btc_usdt_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
btc_usdt_df['timestamp'] = pd.to_datetime(btc_usdt_df['timestamp'], unit='ms')
btc_usdt_df.set_index('timestamp', inplace=True)

# Definir la estrategia de cruce de medias móviles
def moving_average_crossover_strategy(df, short_window=50, long_window=200):
    # Calcular las medias móviles
    df['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    
    # Generar señales de compra y venta
    df['signal'] = 0
    df['signal'][short_window:] = np.where(df['short_mavg'][short_window:] > df['long_mavg'][short_window:], 1, 0)
    df['positions'] = df['signal'].diff()
    
    return df

# Aplicar la estrategia de trading al par BTC/USDT
btc_usdt_df = moving_average_crossover_strategy(btc_usdt_df)

# Imprimir los resultados
print(btc_usdt_df.tail())
