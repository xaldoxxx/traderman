import pandas as pd
import ccxt
import ta
import apis


# Obtener datos históricos
symbol = 'BTC/USDT'
timeframe = '1m'
bybit = ccxt.bybit({
    'apiKey': apis.apiKey,
    'secret': apis.secret,
    })
candlesticks = bybit.fetch_ohlcv(symbol, timeframe)
df = pd.DataFrame(candlesticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Calcular MACD
window_slow = 26
window_fast = 12
window_sign = 9

df['macd'] = ta.trend.macd(df['close'], window_slow=window_slow, window_fast=window_fast, fillna=False)
df['macd_signal'] = ta.trend.macd_signal(df['close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)
df['macd_diff'] = ta.trend.macd_diff(df['close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)

# Guardar en CSV
df.to_csv('historical_data_with_macd.csv')

# Mostrar DataFrame
print(df.tail())

# Función para generar recomendaciones basada en MACD
def generar_recomendaciones_macd(df):
    recomendaciones = []

    # MACD
    macd_recom = "Neutral"
    if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
        macd_recom = "Compra"
    elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
        macd_recom = "Venta"
    recomendaciones.append(f"MACD: {macd_recom}")

    return recomendaciones

# Generar recomendaciones
recomendaciones = generar_recomendaciones_macd(df)

# Mostrar recomendaciones en consola
print("\nRecomendaciones:")
for recomendacion in recomendaciones:
    print(recomendacion)
