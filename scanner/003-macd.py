# itera por sobre las monedas de bybit hasta obtener alguna posibilidad de compora



import pandas as pd
import ccxt
import ta
import apis

# Configurar la conexión con Bybit
exchange = ccxt.bybit({
    'apiKey': apis.apiKey,
    'secret': apis.secret,
})

# Obtener todos los tickers disponibles en Bybit
tickers = exchange.load_markets().keys()

# Parámetros MACD
window_slow = 26
window_fast = 12
window_sign = 9

# Función para generar recomendaciones basada en MACD
def generar_recomendaciones_macd(df):
    recomendaciones = []

    # MACD y señal de línea cruzadas
    macd_recom = "Neutral"
    if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
        macd_recom = "Compra"
    elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
        macd_recom = "Venta"
    recomendaciones.append(f"MACD Crossover: {macd_recom}")

    # Posición del histograma
    hist_recom = "Neutral"
    if df['macd_diff'].iloc[-1] > 0:
        hist_recom = "Tendencia Alcista"
    elif df['macd_diff'].iloc[-1] < 0:
        hist_recom = "Tendencia Bajista"
    recomendaciones.append(f"Histograma: {hist_recom}")

    # Fuerza de la tendencia
    tendencia_recom = "Neutral"
    if df['macd_diff'].iloc[-1] > 0 and df['macd_diff'].iloc[-1] > df['macd_diff'].iloc[-2]:
        tendencia_recom = "Fuerte Tendencia Alcista"
    elif df['macd_diff'].iloc[-1] < 0 and df['macd_diff'].iloc[-1] < df['macd_diff'].iloc[-2]:
        tendencia_recom = "Fuerte Tendencia Bajista"
    recomendaciones.append(f"Fuerza de Tendencia: {tendencia_recom}")

    return recomendaciones

# Iterar por cada ticker
for symbol in tickers:
    try:
        # Obtener datos históricos
        timeframe = '1m'
        candlesticks = exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(candlesticks, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Calcular MACD
        df['macd'] = ta.trend.macd(df['close'], window_slow=window_slow, window_fast=window_fast, fillna=False)
        df['macd_signal'] = ta.trend.macd_signal(df['close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)
        df['macd_diff'] = ta.trend.macd_diff(df['close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)

        # Generar recomendaciones
        recomendaciones = generar_recomendaciones_macd(df)

        # Mostrar recomendaciones en consola
        print(f"\nRecomendaciones para {symbol}:")
        for recomendacion in recomendaciones:
            print(recomendacion)

        # Verificar si hay una señal de compra y detener la iteración
        if "MACD Crossover: Compra" in recomendaciones:
            print(f"Primer MACD Crossover: Compra encontrado para {symbol}")
            break

    except Exception as e:
        print(f"Error al procesar {symbol}: {e}")
