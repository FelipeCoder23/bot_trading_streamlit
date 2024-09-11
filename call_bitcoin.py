import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Definimos la función
def importar_base_bitcoin():
    # Definir la variable global para el dataframe
    global df_bitcoin
    
    # Obtener la fecha actual y la fecha de hace 7 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Convertir las fechas a strings en formato 'YYYY-MM-DD'
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Descargar los datos de Bitcoin desde el rango de fechas
    df_bitcoin = yf.download(tickers='BTC-USD', start=start_str, end=end_str, interval='5m')
    
    # Mostrar un resumen de los datos descargados
    print(df_bitcoin.head())

# Llamar a la función para extraer y mostrar los datos
importar_base_bitcoin()
