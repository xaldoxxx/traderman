import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

class EstrategiaTrading:
    def __init__(self, simbolo, fecha_inicio, fecha_fin):
        self.simbolo = simbolo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.capital_total = 20  # Capital total disponible para trading

        # Llamar a la simulación retroactiva al inicializar la estrategia
        self.simular_trading_retroactivo()

    def descargar_datos(self):
        return yf.download(self.simbolo, start=self.fecha_inicio, end=self.fecha_fin, interval='1m')

    def calcular_bbands(self, df):
        bbands = ta.bbands(df['Close'], length=20, std=2)  # Bandas de Bollinger con una longitud de 20 y un multiplicador de 2 para la desviación estándar
        df['BBANDS_Superior'] = bbands['BBU_20_2.0']
        df['BBANDS_Medio'] = bbands['BBM_20_2.0']
        df['BBANDS_Inferior'] = bbands['BBL_20_2.0']
        return df

    def visualizar_datos(self, df):
        fig = go.Figure()

        # Agregar velas japonesas al gráfico
        fig.add_trace(go.Candlestick(x=df.index,
                                      open=df['Open'],
                                      high=df['High'],
                                      low=df['Low'],
                                      close=df['Close'], name='Precio Histórico'))

        # Agregar bandas de Bollinger al gráfico
        fig.add_trace(go.Scatter(x=df.index, y=df['BBANDS_Superior'], mode='lines', name='BBANDS Superior', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['BBANDS_Medio'], mode='lines', name='BBANDS Medio', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=df.index, y=df['BBANDS_Inferior'], mode='lines', name='BBANDS Inferior', line=dict(color='red')))

        # Agregar precio histórico al gráfico
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Precio Histórico', line=dict(color='green')))

        fig.update_layout(title='Precio Histórico con Bandas de Bollinger',
                          xaxis_rangeslider_visible=False)
        fig.show()

    def simular_trading_retroactivo(self):
        df = self.descargar_datos()
        if not df.empty:
            df = self.calcular_bbands(df)
            self.visualizar_datos(df)
        else:
            print("No se pueden realizar simulaciones porque el DataFrame está vacío.")

# Configuración de parámetros
simbolo = "BTC-USD"   #@param ['AAVE-USD', 'ADA-USD', 'ALGO-USD', 'ARB-USD', 'AVAX-USD', 'AXS-USD', 'BNB-USD', 'BTC-USD', 'DAI-USD', 'DOGE-USD', 'DOT-USD', 'ENS-USD', 'ETH-USD', 'FTM-USD', 'LTC-USD', 'LUNA-USD', 'LUNA-USD', 'MANA-USD', 'MATIC-USD', 'NEAR-USD', 'OP-USD', 'PAXG-USD', 'SAND-USD', 'SLP-USD', 'SOL-USD', 'TRX-USD', 'TRX-USD', 'UNI-USD', 'USDC-USD', 'USDT-USD', 'XLM-USD']
dias = "7"  #@param ["59", "15", "7", "1"]
intervalo = "15m" #@param ["1m", "5m", "15m", "1d"]

fecha_inicio = datetime.now() - timedelta(days=int(dias))
fecha_fin = datetime.now()

# Crear instancia de la estrategia de trading
estrategia = EstrategiaTrading(simbolo, fecha_inicio, fecha_fin)
