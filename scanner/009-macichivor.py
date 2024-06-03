# 009-macichivor.py
# busca los 10 pares usd con fuerte tendencia alcista, estabkece SLTP
# si macd es true para a ichimoku y vortex
# falta realizar la orden y monitorealo en tiempo real

# 007-macd.py
import pandas as pd
import ccxt
import ta
import apis
import logging
import time
from datetime import datetime, timezone, timedelta

# Configurar la conexión con Bybit
exchange = ccxt.bybit({
    'apiKey': apis.apiKey,
    'secret': apis.secret,
})

# Obtener todos los tickers disponibles en Bybit
tickers = exchange.load_markets().keys()
usdt_tickers = [ticker for ticker in tickers if ticker.endswith('/USDT')]

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

# Lista para almacenar los primeros 10 tickers con las condiciones específicas
resultados = []

# Iterar por cada ticker de USDT
for symbol in usdt_tickers:
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

        # Verificar si hay una señal de compra y tendencia alcista
        if "MACD Crossover: Compra" in recomendaciones and "Histograma: Tendencia Alcista" in recomendaciones:
            resultados.append((symbol, recomendaciones))
            if len(resultados) >= 10:
                break

    except Exception as e:
        print(f"Error al procesar {symbol}: {e}")

# Mostrar los resultados
print("\nPrimeros 10 tickers con 'MACD Crossover: Compra' y 'Histograma: Tendencia Alcista':")
for ticker, recoms in resultados:
    print(f"\nTicker: {ticker}")
    for recom in recoms:
        print(recom)

# 005-ichivor.py
import logging
import time
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class TradingRecommendation:
    def __init__(self, df):
        self.df = df

    def calculate_vortex_indicator(self):
        vortex = ta.trend.VortexIndicator(self.df['High'], self.df['Low'], self.df['Close'])
        return vortex.vortex_indicator_pos(), vortex.vortex_indicator_neg()

    def generate_trading_recommendation(self):
        positive_vi, negative_vi = self.calculate_vortex_indicator()
        last_positive_vi = positive_vi.iloc[-1]
        last_negative_vi = negative_vi.iloc[-1]

        # Calcular porcentajes
        total_vi = last_positive_vi + last_negative_vi
        if total_vi == 0:
            return "Mantener"

        positive_vi_percentage = last_positive_vi / total_vi * 100
        negative_vi_percentage = last_negative_vi / total_vi * 100

        # Identificación de tendencias
        if last_positive_vi > last_negative_vi:
            trend = "Alcista"
            trend_percentage = positive_vi_percentage
            trading_recommendation = "Comprar"
        elif last_positive_vi < last_negative_vi:
            trend = "Bajista"
            trend_percentage = negative_vi_percentage
            trading_recommendation = "Vender"
        else:
            trend = "Sin tendencia"
            trend_percentage = 0
            trading_recommendation = "Mantener"

        # Confirmación de señales
        signal_confirmation = "Confirmada" if (trend == "Alcista" and trading_recommendation == "Comprar") or (trend == "Bajista" and trading_recommendation == "Vender") else "No confirmada"

        # Gestión de riesgo
        risk_management = "Salir de la posición" if (trend == "Alcista" and trading_recommendation == "Vender") or (trend == "Bajista" and trading_recommendation == "Comprar") else "Mantener la posición"

        # Logging
        logging.info(f"Tendencia: {trend} ({trend_percentage:.2f}%)")
        logging.info(f"Confirmación de señales: {signal_confirmation}")
        logging.info(f"Gestión de riesgo: {risk_management}")

        return trading_recommendation

class IchimokuChart:
    def __init__(self, df):
        self.df = df

    def calculate_ichimoku(self):
        """Calcular los componentes del Ichimoku."""
        high = self.df['High']
        low = self.df['Low']
        ichimoku = ta.trend.IchimokuIndicator(high=high, low=low)
        self.df['Conversion Line'] = ichimoku.ichimoku_conversion_line()
        self.df['Base Line'] = ichimoku.ichimoku_base_line()
        self.df['Leading Span A'] = ichimoku.ichimoku_a()
        self.df['Leading Span B'] = ichimoku.ichimoku_b()

    def get_signals(self):
        """Obtener señales y niveles de soporte y resistencia."""
        self.calculate_ichimoku()

        current_close = self.df['Close'].iloc[-1]
        conversion_line = self.df['Conversion Line'].iloc[-1]
        base_line = self.df['Base Line'].iloc[-1]
        leading_span_a = self.df['Leading Span A'].iloc[-1]
        leading_span_b = self.df['Leading Span B'].iloc[-1]

        # Identificar niveles de soporte y resistencia
        resistance_level = self.df['Leading Span A'].max()
        support_level = self.df['Leading Span B'].min()

        # Lógica mejorada para Stop Loss y Take Profit
        if current_close > conversion_line and conversion_line > base_line:
            stop_loss = support_level
            take_profit = resistance_level
        elif current_close < conversion_line and conversion_line < base_line:
            stop_loss = resistance_level
            take_profit = support_level
        elif current_close > conversion_line and conversion_line < base_line:
            stop_loss = leading_span_b
            take_profit = leading_span_a
        elif current_close < conversion_line and conversion_line > base_line:
            stop_loss = leading_span_a
            take_profit = leading_span_b
        else:
            stop_loss = None
            take_profit = None

        return {
            'Current Close': current_close,
            'Conversion Line': conversion_line,
            'Base Line': base_line,
            'Leading Span A': leading_span_a,
            'Leading Span B': leading_span_b,
            'Resistance Level': resistance_level,
            'Support Level': support_level,
            'Stop Loss': stop_loss,
            'Take Profit': take_profit
        }

def fetch_ohlcv(symbol, timeframe):
    bybit = ccxt.bybit({
        'apiKey': apis.apiKey,
        'secret': apis.secret,
    })
    try:
        df = pd.DataFrame(bybit.fetch_ohlcv(symbol, timeframe), columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Validación para asegurar que los datos son recientes
        now = datetime.now(timezone.utc)
        last_data_time = df.index[-1].replace(tzinfo=timezone.utc)
        if (now - last_data_time) > timedelta(minutes=int(timeframe[:-1])):
            raise ValueError("Los datos no son recientes.")

        return df
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Devuelve un DataFrame vacío en caso de error

def main():
    tickers = [ticker for ticker, _ in resultados]
    timeframes = {'1m': 1, '5m': 2, '15m': 3}  # Asignar diferentes ponderaciones

    while True:
        for symbol in tickers:
            recommendations = []
            ichimoku_signals = None
            for timeframe, weight in timeframes.items():
                df = fetch_ohlcv(symbol, timeframe)
                if not df.empty:
                    recommendation = TradingRecommendation(df)
                    trading_recommendation = recommendation.generate_trading_recommendation()
                    recommendations.extend([trading_recommendation] * weight)

                    if timeframe == '5m':  # Usar el marco de tiempo de 5 minutos para Ichimoku
                        ichimoku = IchimokuChart(df)
                        ichimoku_signals = ichimoku.get_signals()

            if recommendations.count('Comprar') > recommendations.count('Vender'):
                final_recommendation = 'Comprar'
            elif recommendations.count('Vender') > recommendations.count('Comprar'):
                final_recommendation = 'Vender'
            else:
                final_recommendation = 'Mantener'

            logging.info(f"Final Trading Recommendation for {symbol}: {final_recommendation}")

            if ichimoku_signals:
                logging.info(f"Final Trading Recommendation for {symbol}: {final_recommendation}")
                logging.info(f"Ichimoku Signals for {symbol}: {ichimoku_signals}")
                logging.info(f"Stop Loss: {ichimoku_signals['Stop Loss']}")
                logging.info(f"Take Profit: {ichimoku_signals['Take Profit']}")

        # Esperar antes de la siguiente iteración
        time.sleep(10)  # Reducir el tiempo de espera para scalping

if __name__ == "__main__":
    main()
