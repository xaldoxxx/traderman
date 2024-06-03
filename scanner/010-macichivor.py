#010-macichivor.py
import pandas as pd
import ccxt
import ta
import apis
import logging
from datetime import datetime, timezone, timedelta

def fetch_ohlcv(symbol, timeframe):
    try:
        bybit = ccxt.bybit({
            'apiKey': apis.apiKey,
            'secret': apis.secret,
        })
        ohlcv_data = bybit.fetch_ohlcv(symbol, timeframe)
        
        if not ohlcv_data:
            raise ValueError("No se han obtenido datos OHLCV para el símbolo proporcionado.")
        
        df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        now = datetime.now(timezone.utc)
        last_data_time = df.index[-1].replace(tzinfo=timezone.utc)
        if (now - last_data_time) > timedelta(minutes=int(timeframe[:-1])):
            raise ValueError("Los datos no son recientes.")
        
        return df
    except Exception as e:
        logging.error(f"Error al obtener datos OHLCV para {symbol}: {e}")
        return pd.DataFrame()

exchange = ccxt.bybit({
    'apiKey': apis.apiKey,
    'secret': apis.secret,
})

tickers = exchange.load_markets().keys()
usdt_tickers = [ticker for ticker in tickers if ticker.endswith('/USDT')]

window_slow = 26
window_fast = 12
window_sign = 9

def generar_recomendaciones_macd(df):
    recomendaciones = []

    macd_recom = "Neutral"
    if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
        macd_recom = "Compra"
    elif df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
        macd_recom = "Venta"
    recomendaciones.append(f"MACD Crossover: {macd_recom}")

    hist_recom = "Neutral"
    if df['macd_diff'].iloc[-1] > 0:
        hist_recom = "Tendencia Alcista"
    elif df['macd_diff'].iloc[-1] < 0:
        hist_recom = "Tendencia Bajista"
    recomendaciones.append(f"Histograma: {hist_recom}")

    tendencia_recom = "Neutral"
    if df['macd_diff'].iloc[-1] > 0 and df['macd_diff'].iloc[-1] > df['macd_diff'].iloc[-2]:
        tendencia_recom = "Fuerte Tendencia Alcista"
    elif df['macd_diff'].iloc[-1] < 0 and df['macd_diff'].iloc[-1] < df['macd_diff'].iloc[-2]:
        tendencia_recom = "Fuerte Tendencia Bajista"
    recomendaciones.append(f"Fuerza de Tendencia: {tendencia_recom}")

    return recomendaciones

def calcular_vortex(df):
    vortex = ta.trend.VortexIndicator(df['High'], df['Low'], df['Close'])
    return vortex.vortex_indicator_pos(), vortex.vortex_indicator_neg()

def calcular_ichimoku(df):
    high = df['High']
    low = df['Low']
    ichimoku = ta.trend.IchimokuIndicator(high=high, low=low)
    df['Conversion Line'] = ichimoku.ichimoku_conversion_line()
    df['Base Line'] = ichimoku.ichimoku_base_line()
    df['Leading Span A'] = ichimoku.ichimoku_a()
    df['Leading Span B'] = ichimoku.ichimoku_b()

    current_close = df['Close'].iloc[-1]
    conversion_line = df['Conversion Line'].iloc[-1]
    base_line = df['Base Line'].iloc[-1]
    leading_span_a = df['Leading Span A'].iloc[-1]
    leading_span_b = df['Leading Span B'].iloc[-1]

    resistance_level = df['Leading Span A'].max()
    support_level = df['Leading Span B'].min()

    return {
        'Current Close': current_close,
        'Conversion Line': conversion_line,
        'Base Line': base_line,
        'Leading Span A': leading_span_a,
        'Leading Span B': leading_span_b,
        'Resistance Level': resistance_level,
        'Support Level': support_level,
    }

resultados = []
max_results = 10

for symbol in usdt_tickers:
    if len(resultados) >= max_results:
        break
    try:
        timeframe = '1m'
        df = fetch_ohlcv(symbol, timeframe)

        if df.empty:
            continue

        df['macd'] = ta.trend.macd(df['Close'], window_slow=window_slow, window_fast=window_fast, fillna=False)
        df['macd_signal'] = ta.trend.macd_signal(df['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)
        df['macd_diff'] = ta.trend.macd_diff(df['Close'], window_slow=window_slow, window_fast=window_fast, window_sign=window_sign, fillna=False)

        recomendaciones_macd = generar_recomendaciones_macd(df)

        if ("MACD Crossover: Compra" in recomendaciones_macd and
            "Histograma: Tendencia Alcista" in recomendaciones_macd and
            "Fuerza de Tendencia: Fuerte Tendencia Alcista" in recomendaciones_macd):
            
            positive_vi, negative_vi = calcular_vortex(df)
            last_positive_vi = positive_vi.iloc[-1]
            last_negative_vi = negative_vi.iloc[-1]

            ichimoku_data = calcular_ichimoku(df)

            if last_positive_vi > last_negative_vi:
                trading_recommendation = "Comprar"
                signal_confirmation = "Confirmada"
            else:
                trading_recommendation = "Vender"
                signal_confirmation = "No confirmada"

            if trading_recommendation == "Comprar" and signal_confirmation == "Confirmada":
                resultados.append((symbol, ichimoku_data['Support Level'], ichimoku_data['Resistance Level']))
                
                # Imprimir información en consola
                print(f"Par: {symbol}, Stop Loss: {ichimoku_data['Support Level']}, Take Profit: {ichimoku_data['Resistance Level']}")

    except Exception as e:
        print(f"Error al procesar {symbol}: {e}")
        continue

print("\nResultados finales:")
for par, stop_loss, take_profit in resultados:
    print(f"Par: {par}, Stop Loss: {stop_loss}, Take Profit: {take_profit}")
