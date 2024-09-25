# Importar librerías
import yfinance as yf
from bs4 import BeautifulSoup
import requests
import plotly.graph_objects as go
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

import matplotlib.pyplot as plt
plt.rc('figure', figsize = (5, 5))

import time
from datetime import datetime, timedelta
from IPython.display import clear_output

import seaborn as sns
import numpy as np

# Variables globales
global df_bitcoin, df_bitcoin_limpio, precio_actual, tendencia, media_bitcoin, algoritmo_decision, color

def importar_base_bitcoin():
    global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision, color

    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Descargar datos de Bitcoin usando yfinance
    df_bitcoin = yf.download("BTC-USD", start=start_date, end=end_date, interval="5m")

    # Verificar si se descargaron los datos
    if df_bitcoin.empty:
        print("No se descargaron datos. Verifica el rango de fechas o la conexión a internet.")
    else:
        print("Datos descargados correctamente.")


def extraer_tendencias():
    global precio_actual, tendencia, media_bitcoin, algoritmo_decision, color

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    url = 'https://coinmarketcap.com/currencies/bitcoin/'

    # Realizar la solicitud y parsear el contenido con BeautifulSoup
    respuesta = requests.get(url, headers=headers)
    s = BeautifulSoup(respuesta.content, 'html.parser')

    # 1. Extraer el precio actual de Bitcoin
    precio_tag = s.find("span", {"data-test": "text-cdp-price-display"})
    if precio_tag:
        precio_actual = float(precio_tag.getText().replace('$', '').replace(',', ''))
    else:
        precio_actual = None

    # 2. Extraer la tendencia del precio (alta o baja)
    tendencia_tag = s.find("p", {"color": True, "data-change": True})
    if tendencia_tag:
        color = tendencia_tag['color']
        if color == "green":
            tendencia = 'alta'  # Tendencia alcista
        elif color == "red":
            tendencia = 'baja'  # Tendencia bajista
        else:
            tendencia = None
    else:
        tendencia = None

    # Retornar el precio actual y la tendencia
    return precio_actual, tendencia

def limpieza_datos():
    global df_bitcoin, df_bitcoin_limpio, media_bitcoin

    # Número inicial de datos
    num_datos_inicial = df_bitcoin.shape[0]
    print(f"Número inicial de datos: {num_datos_inicial}")

    # Copiar el DataFrame original para no modificarlo directamente
    df_bitcoin_limpio = df_bitcoin.copy()

    # Paso 1: Eliminar índices duplicados
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]
    print(f"Duplicados eliminados: {num_datos_inicial - df_bitcoin_limpio.shape[0]}")

    # Paso 2: Rellenar valores nulos en la columna 'Close' con el último valor válido
    df_bitcoin_limpio['Close'] = df_bitcoin_limpio['Close'].ffill()

    # Paso 3: Eliminar filas donde el volumen sea menor o igual a cero
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]

    # Paso 4: Calcular Q1, Q3 y el IQR de 'Close'
    valor = df_bitcoin_limpio['Close']
    Q1 = valor.quantile(0.25)
    Q3 = valor.quantile(0.75)
    IQR = Q3 - Q1
    limite_inferior = Q1 - 1.5 * IQR
    limite_superior = Q3 + 1.5 * IQR
    print(f"Límites de eliminación de outliers: Inferior={limite_inferior}, Superior={limite_superior}")

    # Paso 5: Seleccionar solo los registros dentro de los límites del IQR
    df_bitcoin_limpio = df_bitcoin_limpio[(valor >= limite_inferior) & (valor <= limite_superior)]

    # Paso 6: Calcular el precio promedio de Bitcoin después de la limpieza
    media_bitcoin = round(df_bitcoin_limpio['Close'].mean(), 0)

    # Número final de datos
    num_datos_final = df_bitcoin_limpio.shape[0]
    datos_eliminados = num_datos_inicial - num_datos_final

    # Reporte final
    print(f"Número final de datos: {num_datos_final}")
    print(f"Datos eliminados durante la limpieza: {datos_eliminados}")

def calcular_sma():
    global df_bitcoin_limpio

    # Calcular la SMA de corto plazo (por ejemplo, 10 periodos)
    df_bitcoin_limpio['SMA_corto'] = df_bitcoin_limpio['Close'].rolling(window=10).mean()

    # Calcular la SMA de largo plazo (por ejemplo, 50 periodos)
    df_bitcoin_limpio['SMA_largo'] = df_bitcoin_limpio['Close'].rolling(window=50).mean()

def tomar_decisiones():
    global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision, color

    # Obtener las últimas SMA calculadas en el DataFrame df_bitcoin_limpio
    sma_corto_actual = df_bitcoin_limpio['SMA_corto'].iloc[-1]
    sma_largo_actual = df_bitcoin_limpio['SMA_largo'].iloc[-1]

    # Imprimir los valores clave
    print(f"Valores claves:")
    print(f"  - SMA corto actual: {sma_corto_actual}")
    print(f"  - SMA largo actual: {sma_largo_actual}")
    print(f"  - Precio actual: {precio_actual}")
    print(f"  - Media del precio de Bitcoin: {media_bitcoin}")
    print(f"  - Tendencia: {tendencia}")

    # Algoritmo de decisión basado en SMA y tendencia actuales
    if (sma_corto_actual > sma_largo_actual) and (tendencia == 'alta'):
        algoritmo_decision = 'Comprar'
        color = '#228b22'  # Verde, señal de compra
        print(f"Decisión: {algoritmo_decision} - SMA corta > SMA larga y tendencia alcista.")

    elif (sma_corto_actual < sma_largo_actual) and (tendencia == 'baja'):
        algoritmo_decision = 'Vender'
        color = '#dc143c'  # Rojo, señal de venta
        print(f"Decisión: {algoritmo_decision} - SMA corta < SMA larga y tendencia bajista.")

    else:
        algoritmo_decision = 'Mantener'
        color = '#000000'  # Negro, señal de mantener
        print(f"Decisión: {algoritmo_decision} - No hay una señal clara.")

# Loop que toma decisiones cada 5 minutos
while True:
    print("Iniciando ciclo de análisis...")

    # Paso 1: Descargar los datos y extraer el precio actual
    importar_base_bitcoin()
    precio_actual, tendencia = extraer_tendencias()

    # Paso 2: Limpiar los datos y calcular las medias móviles
    limpieza_datos()  # Limpieza antes de calcular SMA
    calcular_sma()  # Calcular medias móviles

    # Paso 3: Tomar la decisión de compra/venta
    tomar_decisiones()

    # Paso 4: Mostrar la decisión y el color asociado
    print(f"Decisión: {algoritmo_decision} (Color: {color})")

    # Paso 5: Esperar 5 minutos antes de volver a ejecutar el loop
    print("Esperando 5 minutos antes de la siguiente decisión...")
    time.sleep(300)  # Pausar por 300 segundos (5 minutos)
    print("Reiniciando ciclo...\n")
