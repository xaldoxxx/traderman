#005-ichivor.py
import apis
import ccxt
import pandas as pd
import ta
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
    symbol = 'BTC/USDT'
    timeframes = {'1m': 1, '5m': 2, '15m': 3}  # Asignar diferentes ponderaciones

    while True:
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

        logging.info(f"Final Trading Recommendation: {final_recommendation}")

        if ichimoku_signals:
            logging.info(f"Ichimoku Signals: {ichimoku_signals}")
            logging.info(f"Stop Loss: {ichimoku_signals['Stop Loss']}")
            logging.info(f"Take Profit: {ichimoku_signals['Take Profit']}")

        # Aquí podrías añadir el código para ejecutar las órdenes en el intercambio
        # ejecutar_orden(final_recommendation)

        # Esperar antes de la siguiente iteración
        time.sleep(3)  # Reducir el tiempo de espera para scalping

if __name__ == "__main__":
    main()
