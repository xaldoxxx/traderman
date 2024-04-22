
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

# Definir la función para calcular el MACD
def calculate_macd(df, short_window=12, long_window=26, signal_window=9):
    exp1 = df['close'].ewm(span=short_window, adjust=False).mean()
    exp2 = df['close'].ewm(span=long_window, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal

# Definir la función para imprimir el mensaje de compra o venta basado en el cruce de los valores MACD y señal
def print_buy_sell_signal(macd, signal):
    if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
        print("Se recomienda comprar. El MACD ha cruzado por encima de la señal.")
    elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
        print("Se recomienda vender. El MACD ha cruzado por debajo de la señal.")
    else:
        print("No se recomienda comprar ni vender en este momento.")

# Calcular el MACD y la señal y agregarlos al DataFrame
macd, signal = calculate_macd(btc_usdt_df)
btc_usdt_df['macd'] = macd
btc_usdt_df['signal'] = signal

# Imprimir los resultados
print(btc_usdt_df.tail())

# Imprimir el mensaje de compra o venta basado en el cruce de los valores MACD y señal
print_buy_sell_signal(macd, signal)
