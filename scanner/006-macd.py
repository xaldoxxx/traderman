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

# Parámetros MACD y otros indicadores
window_slow = 26
window_fast = 12
window_sign = 9
smma_period = 365
williams_period = 28

# Función para generar recomendaciones basada en MACD y otras condiciones
def generar_recomendaciones_macd(df):
    recomendaciones = []

    # Calcular indicadores adicionales
    df['smma'] = df['close'].rolling(window=smma_period, min_periods=1).mean()
    df['williams_r'] = ta.momentum.williams_r(df['high'], df['low'], df['close'], lbp=williams_period, fillna=False)

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

    # Condiciones de compra
    if df['close'].iloc[-1] > df['smma'].iloc[-1] and df['macd'].iloc[-1] < 0 and df['williams_r'].iloc[-1] > -80 and df['williams_r'].iloc[-2] <= -80:
        recomendaciones.append("Compra Condicional: Comprar")

    # Condiciones de venta
    if df['close'].iloc[-1] < df['smma'].iloc[-1] and df['macd'].iloc[-1] > 0 and df['williams_r'].iloc[-1] < -20 and df['williams_r'].iloc[-2] >= -20:
        recomendaciones.append("Venta Condicional: Vender")

    return recomendaciones

# Lista para almacenar los primeros 10 tickers con las condiciones específicas
resultados = []

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

        # Verificar si hay una señal de compra y fuerte tendencia alcista
        if "MACD Crossover: Compra" in recomendaciones and "Fuerza de Tendencia: Fuerte Tendencia Alcista" in recomendaciones:
            resultados.append((symbol, recomendaciones))
            if len(resultados) >= 10:
                break

    except Exception as e:
        print(f"Error al procesar {symbol}: {e}")

# Mostrar los resultados
print("\nPrimeros 10 tickers con 'MACD Crossover: Compra' y 'Fuerza de Tendencia: Fuerte Tendencia Alcista':")
for ticker, recoms in resultados:
    print(f"\nTicker: {ticker}")
    for recom in recoms:
        print(recom)
