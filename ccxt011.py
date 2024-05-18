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

    def obtener_ohlcv(self, simbolo, intervalo, desde=None, limite=1000):
        """
        Obtiene los datos de OHLCV desde el intercambio.

        Parámetros:
        -----------
        simbolo : str
            El símbolo del mercado.
        intervalo : str
            El intervalo de tiempo para las velas.
        desde : int, opcional
            La fecha de inicio en milisegundos. Por defecto es None.
        limite : int
            Número de velas a obtener.

        Retorna:
        --------
        list
            Lista de datos de OHLCV.
        """
        return self.intercambio.fetch_ohlcv(simbolo, intervalo, since=desde, limit=limite)


class ScraperOHLCV:
    """
    Clase para manejar la obtención de datos de OHLCV de manera iterativa.

    Métodos:
    --------
    obtener_todos_ohlcv(simbolo, intervalo, desde, limite)
        Obtiene todos los datos de OHLCV desde la fecha proporcionada.
    """

    def __init__(self, intercambio_id):
        """
        Inicializa la clase ScraperOHLCV con el identificador de intercambio proporcionado.
        """
        self.intercambio = Intercambio(intercambio_id)

    def obtener_todos_ohlcv(self, simbolo, intervalo, desde, limite=1000):
        """
        Obtiene todos los datos de OHLCV desde la fecha proporcionada.

        Parámetros:
        -----------
        simbolo : str
            El símbolo del mercado.
        intervalo : str
            El intervalo de tiempo para las velas.
        desde : str
            La fecha de inicio en formato string.
        limite : int
            Número de velas a obtener por cada solicitud.

        Retorna:
        --------
        list
            Lista de datos de OHLCV.
        """
        desde_timestamp = self.intercambio.parsear_fecha(desde)
        ohlcv_list = []
        ohlcv = self.intercambio.obtener_ohlcv(simbolo, intervalo, desde_timestamp, limite)
        ohlcv_list.extend(ohlcv)

        while True:
            desde_timestamp = ohlcv[-1][0]
            nuevo_ohlcv = self.intercambio.obtener_ohlcv(simbolo, intervalo, desde_timestamp, limite)
            ohlcv.extend(nuevo_ohlcv)
            if len(nuevo_ohlcv) < limite:
                break

        return ohlcv_list

if __name__ == "__main__":
    simbolo = 'BTC/USDT'
    intervalo = '5m'
    desde = '2022-07-21 00:00:00'
    limite = 1000

    scraper = ScraperOHLCV('binance')
    ohlcv_datos = scraper.obtener_todos_ohlcv(simbolo, intervalo, desde, limite)
    print(f'Se obtuvieron {len(ohlcv_datos)} registros de OHLCV.')
