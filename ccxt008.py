'''
El RSI es un indicador técnico que se utiliza comúnmente en análisis técnico para evaluar si un activo está
sobrecomprado o sobrevendido. Se calcula utilizando la fórmula estándar que considera las ganancias y pérdidas
promedio durante un período de tiempo específico.

En general, un RSI por encima de 70 se considera que el activo está sobrecomprado, lo que sugiere que puede
haber una corrección a la baja en el precio. Por otro lado, un RSI por debajo de 30 se considera que el activo
está sobrevendido, lo que sugiere que puede haber una corrección al alza en el precio.
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
    df['rsi'] = rsi  # Agregar el RSI al DataFrame
    return df

# Definir la función para imprimir el mensaje de compra o venta basado en el RSI
def print_buy_sell_signal(rsi_value):
    if rsi_value > 70:
        print("El RSI es {}. Se recomienda vender.".format(rsi_value))
    elif rsi_value < 30:
        print("El RSI es {}. Se recomienda comprar.".format(rsi_value))
    else:
        print("El RSI es {}. No se recomienda comprar ni vender en este momento.".format(rsi_value))

# Calcular el RSI y agregarlo al DataFrame
rsi_value = calculate_rsi(btc_usdt_df)['rsi'].iloc[-1]  # Obtener el valor del RSI más reciente
print_buy_sell_signal(rsi_value)
