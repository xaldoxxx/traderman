'''
calculamos el RSI (Índice de Fuerza Relativa) utilizando los precios de cierre del par de trading BTC/USDT
en intervalos de 1 hora. La función calculate_rsi() calcula el RSI utilizando la fórmula estándar, y luego
agregamos el RSI calculado al DataFrame btc_usdt_df.

Recuerda que el RSI es solo un indicador y se utiliza comúnmente junto con otros indicadores y análisis
técnico para tomar decisiones de trading. Además, puedes ajustar el período del RSI según tus necesidades
y preferencias.
'''
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

# Definir la función para calcular el RSI
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Calcular el RSI y agregarlo al DataFrame
btc_usdt_df['rsi'] = calculate_rsi(btc_usdt_df)

# Imprimir los resultados
print(btc_usdt_df.tail())
