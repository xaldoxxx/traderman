import tkinter as tk
from datetime import datetime, timedelta
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import pandas as pd

class EstrategiaTrading:
    def __init__(self, simbolo, fecha_inicio, fecha_fin):
        self.simbolo = simbolo
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.capital_total = 20  # Capital total disponible para trading

        # Llamar a la simulación retroactiva al inicializar la estrategia
        self.simular_trading_retroactivo()

    def descargar_datos(self):
        data = pd.DataFrame()
        delta = timedelta(days=7)
        start_date = self.fecha_inicio
        end_date = min(start_date + delta, self.fecha_fin)

        while start_date < self.fecha_fin:
            try:
                partial_data = yf.download(self.simbolo, start=start_date, end=end_date, interval='1m')
                data = pd.concat([data, partial_data])
            except Exception as e:
                print(f"Error al descargar datos para el rango {start_date} - {end_date}: {e}")

            start_date = end_date + timedelta(minutes=1)
            end_date = min(start_date + delta, self.fecha_fin)

        return data

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

# Función para iniciar la simulación cuando se hace clic en el botón
def iniciar_simulacion():
    simbolo = entry_simbolo.get()
    dias = entry_dias.get()
    intervalo = entry_intervalo.get()

    fecha_inicio = datetime.now() - timedelta(days=int(dias))
    fecha_fin = datetime.now()

    # Crear instancia de la estrategia de trading
    estrategia = EstrategiaTrading(simbolo, fecha_inicio, fecha_fin)

# Crear la ventana principal de la interfaz gráfica
root = tk.Tk()
root.title("Simulador de Estrategia de Trading")

# Opciones limitadas para símbolos, días e intervalo
simbolos = ['AAVE-USD', 'ADA-USD', 'ALGO-USD', 'ARB-USD', 'AVAX-USD', 'AXS-USD', 'BNB-USD', 'BTC-USD', 'DAI-USD', 'DOGE-USD', 'DOT-USD', 'ENS-USD', 'ETH-USD', 'FTM-USD', 'LTC-USD', 'LUNA-USD', 'LUNA-USD', 'MANA-USD', 'MATIC-USD', 'NEAR-USD', 'OP-USD', 'PAXG-USD', 'SAND-USD', 'SLP-USD', 'SOL-USD', 'TRX-USD', 'TRX-USD', 'UNI-USD', 'USDC-USD', 'USDT-USD', 'XLM-USD']
dias = ["59", "15", "7", "1"]
intervalo = ["1m", "5m", "15m", "1d"]

# Crear widgets para ingresar datos
label_simbolo = tk.Label(root, text="Símbolo:")
entry_simbolo = tk.StringVar(value=simbolos[0])
menu_simbolo = tk.OptionMenu(root, entry_simbolo, *simbolos)

label_dias = tk.Label(root, text="Días:")
entry_dias = tk.StringVar(value=dias[0])
menu_dias = tk.OptionMenu(root, entry_dias, *dias)

label_intervalo = tk.Label(root, text="Intervalo:")
entry_intervalo = tk.StringVar(value=intervalo[0])
menu_intervalo = tk.OptionMenu(root, entry_intervalo, *intervalo)

# Crear botón para iniciar la simulación
boton_simular = tk.Button(root, text="Simular", command=iniciar_simulacion)

# Organizar los widgets en la ventana
label_simbolo.grid(row=0, column=0)
menu_simbolo.grid(row=0, column=1)

label_dias.grid(row=1, column=0)
menu_dias.grid(row=1, column=1)

label_intervalo.grid(row=2, column=0)
menu_intervalo.grid(row=2, column=1)

boton_simular.grid(row=3, columnspan=2)

# Ejecutar el bucle principal de tkinter
root.mainloop()
