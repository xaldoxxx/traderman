'''
py -m venv .venv
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate

pip install --upgrade setuptools
pip install yfinance pandas_ta plotly

python script.py

Set-ExecutionPolicy Undefined -Scope CurrentUser
deactivate

Este código permite simular una estrategia de trading retroactivamente utilizando datos financieros
implementando algunos indicadores a partir de datos
históricos y visualizar los resultados en forma de gráfico interactivo
patron de diseño modelo vista controlador
'''

import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
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

    def simular_trading_retroactivo(self, progress_bar):
        progress_bar.start()
        df = self.descargar_datos()
        progress_bar.stop()
        
        if not df.empty:
            df = self.calcular_bbands(df)
            self.visualizar_datos(df)
        else:
            messagebox.showwarning("Advertencia", "No se pueden realizar simulaciones porque el DataFrame está vacío.")

class Vista:
    def __init__(self, root, simbolos, dias, intervalo):
        self.root = root
        self.root.title("Simulador de Estrategia de Trading")
        self.root.configure(bg='#121212')
        
        tk.Label(root, text="Símbolo:", bg='#121212', fg='white').grid(row=0, column=0, padx=10, pady=10)
        tk.Label(root, text="Días:", bg='#121212', fg='white').grid(row=1, column=0, padx=10, pady=10)
        tk.Label(root, text="Intervalo:", bg='#121212', fg='white').grid(row=2, column=0, padx=10, pady=10)

        self.entry_simbolo = tk.StringVar(value=simbolos[0])
        self.entry_dias = tk.StringVar(value=dias[0])
        self.entry_intervalo = tk.StringVar(value=intervalo[0])

        self.menu_simbolo = tk.OptionMenu(root, self.entry_simbolo, *simbolos)
        self.menu_dias = tk.OptionMenu(root, self.entry_dias, *dias)
        self.menu_intervalo = tk.OptionMenu(root, self.entry_intervalo, *intervalo)

        self.menu_simbolo.grid(row=0, column=1, padx=10, pady=10)
        self.menu_dias.grid(row=1, column=1, padx=10, pady=10)
        self.menu_intervalo.grid(row=2, column=1, padx=10, pady=10)

        self.boton_simular = tk.Button(root, text="Simular", command=self.iniciar_simulacion, bg='black', fg='white', relief=tk.FLAT)
        self.boton_simular.grid(row=3, columnspan=2, pady=20)

        self.progress_bar = Progressbar(root, mode='indeterminate', length=200)
        self.progress_bar.grid(row=4, columnspan=2, pady=10)
        self.progress_bar.stop()

    def iniciar_simulacion(self):
        simbolo = self.entry_simbolo.get()
        dias = self.entry_dias.get()
        intervalo = self.entry_intervalo.get()

        fecha_inicio = datetime.now() - timedelta(days=int(dias))
        fecha_fin = datetime.now()

        # Crear instancia de la estrategia de trading
        estrategia = EstrategiaTrading(simbolo, fecha_inicio, fecha_fin)
        estrategia.simular_trading_retroactivo(self.progress_bar)
        
def main():
    root = tk.Tk()
    simbolos = ['AAVE-USD', 'ADA-USD', 'ALGO-USD', 'ARB-USD', 'AVAX-USD', 'AXS-USD', 'BNB-USD', 'BTC-USD', 'DAI-USD', 'DOGE-USD', 'DOT-USD', 'ENS-USD', 'ETH-USD', 'FTM-USD', 'LTC-USD', 'LUNA-USD', 'LUNA-USD', 'MANA-USD', 'MATIC-USD', 'NEAR-USD', 'OP-USD', 'PAXG-USD', 'SAND-USD', 'SLP-USD', 'SOL-USD', 'TRX-USD', 'TRX-USD', 'UNI-USD', 'USDC-USD', 'USDT-USD', 'XLM-USD']
    dias = ["59", "15", "7", "1"]
    intervalo = ["1m", "5m", "15m", "1d"]
    vista = Vista(root, simbolos, dias, intervalo)
    root.mainloop()

if __name__ == "__main__":
    main()
