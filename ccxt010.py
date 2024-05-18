import os
import sys
from pathlib import Path
import csv
import ccxt

class Intercambio:
    """
    Clase para manejar la conexión y la configuración del intercambio.

    Atributos:
    ----------
    intercambio_id : str
        Identificador del intercambio a utilizar.
    """

    def __init__(self, intercambio_id):
        """
        Inicializa la clase Intercambio con el identificador proporcionado.
        """
        self.intercambio_id = intercambio_id
        self.intercambio = self._crear_intercambio()

    def _crear_intercambio(self):
        """
        Crea una instancia del intercambio utilizando ccxt.

        Retorna:
        --------
        ccxt.Exchange
            Instancia del intercambio configurado.
        """
        intercambio = getattr(ccxt, self.intercambio_id)({'enableRateLimit': True})
        intercambio.load_markets()
        return intercambio

    def parsear_fecha(self, fecha):
        """
        Convierte una fecha en formato string a milisegundos.

        Parámetros:
        -----------
        fecha : str
            Fecha en formato string.

        Retorna:
        --------
        int
            Fecha en milisegundos.
        """
        return self.intercambio.parse8601(fecha)

    def obtener_ohlcv(self, simbolo, intervalo, desde, limite, max_reintentos):
        """
        Obtiene los datos de OHLCV desde el intercambio.

        Parámetros:
        -----------
        simbolo : str
            El símbolo del mercado.
        intervalo : str
            El intervalo de tiempo para las velas.
        desde : int
            La fecha de inicio en milisegundos.
        limite : int
            Número de velas a obtener.
        max_reintentos : int
            Número máximo de reintentos en caso de fallo.

        Retorna:
        --------
        list
            Lista de datos de OHLCV.
        """
        return self._intentar_obtener_ohlcv(simbolo, intervalo, desde, limite, max_reintentos)

    def _intentar_obtener_ohlcv(self, simbolo, intervalo, desde, limite, max_reintentos):
        num_reintentos = 0
        while num_reintentos <= max_reintentos:
            try:
                num_reintentos += 1
                ohlcv = self.intercambio.fetch_ohlcv(simbolo, intervalo, desde, limite)
                return ohlcv
            except Exception as e:
                if num_reintentos > max_reintentos:
                    raise Exception(f'Error al obtener OHLCV: {e}')

class EscritorCSV:
    """
    Clase para escribir datos en un archivo CSV.

    Métodos:
    --------
    escribir_a_csv(nombre_archivo, intercambio, datos)
        Escribe los datos proporcionados en un archivo CSV.
    """

    def escribir_a_csv(self, nombre_archivo, intercambio, datos):
        """
        Escribe los datos proporcionados en un archivo CSV.

        Parámetros:
        -----------
        nombre_archivo : str
            Nombre del archivo CSV.
        intercambio : str
            Nombre del intercambio.
        datos : list
            Datos a escribir en el archivo.
        """
        ruta = Path("./data/raw/", str(intercambio))
        ruta.mkdir(parents=True, exist_ok=True)
        ruta_completa = ruta / str(nombre_archivo)
        with ruta_completa.open('w+', newline='') as archivo_salida:
            escritor_csv = csv.writer(archivo_salida, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            escritor_csv.writerows(datos)

class ScraperOHLCV:
    """
    Clase para manejar la obtención y almacenamiento de datos de OHLCV.

    Métodos:
    --------
    obtener_y_guardar_datos(nombre_archivo, intercambio_id, max_reintentos, simbolo, intervalo, desde, limite)
        Obtiene los datos de OHLCV y los guarda en un archivo CSV.
    """

    def __init__(self, intercambio_id):
        """
        Inicializa la clase ScraperOHLCV con el identificador de intercambio proporcionado.
        """
        self.intercambio = Intercambio(intercambio_id)
        self.escritor_csv = EscritorCSV()

    def obtener_y_guardar_datos(self, nombre_archivo, max_reintentos, simbolo, intervalo, desde, limite):
        """
        Obtiene los datos de OHLCV y los guarda en un archivo CSV.

        Parámetros:
        -----------
        nombre_archivo : str
            Nombre del archivo CSV.
        max_reintentos : int
            Número máximo de reintentos en caso de fallo.
        simbolo : str
            El símbolo del mercado.
        intervalo : str
            El intervalo de tiempo para las velas.
        desde : str
            La fecha de inicio en formato string.
        limite : int
            Número de velas a obtener.
        """
        if isinstance(desde, str):
            desde = self.intercambio.parsear_fecha(desde)
        
        ohlcv = self._obtener_todos_ohlcv(simbolo, intervalo, desde, limite, max_reintentos)
        self.escritor_csv.escribir_a_csv(nombre_archivo, self.intercambio.intercambio_id, ohlcv)
        print(f'Se guardaron {len(ohlcv)} velas desde {self.intercambio.intercambio.iso8601(ohlcv[0][0])} hasta {self.intercambio.intercambio.iso8601(ohlcv[-1][0])} en {nombre_archivo}')

    def _obtener_todos_ohlcv(self, simbolo, intervalo, desde, limite, max_reintentos):
        """
        Obtiene todos los datos de OHLCV disponibles desde el intercambio.

        Parámetros:
        -----------
        simbolo : str
            El símbolo del mercado.
        intervalo : str
            El intervalo de tiempo para las velas.
        desde : int
            La fecha de inicio en milisegundos.
        limite : int
            Número de velas a obtener por cada solicitud.
        max_reintentos : int
            Número máximo de reintentos en caso de fallo.

        Retorna:
        --------
        list
            Lista de datos de OHLCV.
        """
        primer_timestamp = self.intercambio.intercambio.milliseconds()
        duracion_intervalo_segundos = self.intercambio.intercambio.parse_timeframe(intervalo)
        duracion_intervalo_ms = duracion_intervalo_segundos * 1000
        delta_tiempo = limite * duracion_intervalo_ms
        todos_ohlcv = []

        while True:
            fetch_desde = primer_timestamp - delta_tiempo
            ohlcv = self.intercambio.obtener_ohlcv(simbolo, intervalo, fetch_desde, limite, max_reintentos)
            if ohlcv[0][0] >= primer_timestamp:
                break
            primer_timestamp = ohlcv[0][0]
            todos_ohlcv = ohlcv + todos_ohlcv
            print(f'{len(todos_ohlcv)} velas de {simbolo} en total desde {self.intercambio.intercambio.iso8601(todos_ohlcv[0][0])} hasta {self.intercambio.intercambio.iso8601(todos_ohlcv[-1][0])}')
            if fetch_desde < desde:
                break
        return todos_ohlcv

if __name__ == "__main__":
    nombre_archivo = 'datos_ohlcv.csv'
    intercambio_id = 'binance'
    max_reintentos = 5
    simbolo = 'BTC/USDT'
    intervalo = '1d'
    desde = '2022-01-01T00:00:00Z'
    limite = 1000

    scraper = ScraperOHLCV(intercambio_id)
    scraper.obtener_y_guardar_datos(nombre_archivo, max_reintentos, simbolo, intervalo, desde, limite)
