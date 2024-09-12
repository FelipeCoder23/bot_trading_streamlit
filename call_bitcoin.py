import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re  # Para expresiones regulares
import plotly.graph_objects as go
import time

# Variables globales
global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision

# Definir la función para importar datos de Bitcoin
def importar_base_bitcoin():
    global df_bitcoin
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Convertir fechas a strings en formato 'YYYY-MM-DD'
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Descargar datos de Bitcoin usando yfinance
    df_bitcoin = yf.download(tickers='BTC-USD', start=start_str, end=end_str, interval='5m')
    
    # Mostrar un resumen de los datos descargados
    print(df_bitcoin.head())

# Definir la función para extraer tendencias de CoinMarketCap
def extraer_tendencias():
    global precio_actual, tendencia
    
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    
    try:
        page = requests.get(url)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extraer el precio actual del Bitcoin
        precio_tag = soup.find("span", {"data-test": "text-cdp-price-display"})
        if precio_tag:
            precio_actual = float(precio_tag.text.replace('$', '').replace(',', ''))
            print(f"Precio actual del Bitcoin: ${precio_actual}")
        else:
            print("No se pudo extraer el precio actual del Bitcoin.")
        
        # Extraer la variación de tendencia en porcentaje
        p_tags = soup.find_all("p")
        for p in p_tags:
            variacion_text = re.search(r"([-+]?\d*\.\d+|\d+)%", p.text)
            if variacion_text:
                variacion = float(variacion_text.group(0).replace('%', ''))
                tendencia = 'baja' if variacion < 0 else 'alta'
                print(f"Variación: {variacion}% - Tendencia: {tendencia}")
                break
        
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la página: {e}")

# Función para limpiar datos
def limpieza_datos():
    global df_bitcoin, media_bitcoin
    
    df_bitcoin_limpio = df_bitcoin.copy()
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]
    df_bitcoin_limpio['Close'] = df_bitcoin_limpio['Close'].ffill()
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]
    
    # Calcular cuartiles y filtrar outliers
    Q1 = df_bitcoin_limpio['Close'].quantile(0.25)
    Q3 = df_bitcoin_limpio['Close'].quantile(0.75)
    IQR = Q3 - Q1
    df_bitcoin_limpio = df_bitcoin_limpio[(df_bitcoin_limpio['Close'] >= Q1) & (df_bitcoin_limpio['Close'] <= Q3)]
    
    # Calcular media del precio
    media_bitcoin = df_bitcoin_limpio['Close'].mean()
    print(f"Precio promedio de Bitcoin después de la limpieza: {media_bitcoin:.2f} USD")

# Función para calcular SMA (Simple Moving Average)
def calcular_sma(periodo_corto=10, periodo_largo=50):
    global df_bitcoin
    # Calcular las medias móviles
    df_bitcoin['SMA_corto'] = df_bitcoin['Close'].rolling(window=periodo_corto).mean()
    df_bitcoin['SMA_largo'] = df_bitcoin['Close'].rolling(window=periodo_largo).mean()

    # Señales de compra/venta basadas en el cruce de SMAs
    df_bitcoin['Signal'] = 0
    df_bitcoin['Signal'] = df_bitcoin.apply(lambda row: 1 if row['SMA_corto'] > row['SMA_largo'] else -1, axis=1)

    # Mostrar las últimas filas con las señales
    print(df_bitcoin[['SMA_corto', 'SMA_largo', 'Signal']].tail())

# Función para tomar decisiones con SMA
def tomar_decisiones_con_sma():
    global df_bitcoin
    # Reglas de compra/venta basadas en SMA
    df_bitcoin['Decision'] = df_bitcoin.apply(lambda row: 'Comprar' if row['SMA_corto'] > row['SMA_largo'] 
                                              else 'Vender', axis=1)
    print(df_bitcoin[['SMA_corto', 'SMA_largo', 'Decision']].tail())

# Función para visualización interactiva con Plotly
def visualizacion_interactiva():
    global df_bitcoin, media_bitcoin, algoritmo_decision
    
    df_bitcoin['Promedio'] = media_bitcoin
    
    # Crear una figura para el gráfico
    fig = go.Figure()
    
    # Agregar línea del precio de cierre
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['Close'], mode='lines', name='Precio de Cierre', line=dict(color='blue')))
    
    # Agregar línea del precio promedio
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['SMA_corto'], mode='lines', name='SMA Corto', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['SMA_largo'], mode='lines', name='SMA Largo', line=dict(color='red', dash='dash')))
    
    # Configurar título y etiquetas
    fig.update_layout(title='Evolución del Precio del Bitcoin con SMA',
                      xaxis_title='Fecha',
                      yaxis_title='Precio en USD')
    
    # Mostrar el gráfico
    fig.show()

# Bucle de automatización
while True:
    try:
        importar_base_bitcoin()    # Paso 1: Obtener datos históricos de Bitcoin
        extraer_tendencias()       # Paso 2: Extraer tendencia del sitio web
        limpieza_datos()           # Paso 3: Limpiar y procesar los datos
        calcular_sma()             # Paso 4: Calcular las SMA y generar señales
        tomar_decisiones_con_sma() # Paso 5: Tomar decisiones basadas en SMA
        visualizacion_interactiva()# Paso 6: Mostrar el gráfico interactivo con Plotly

        # Pausa de 5 minutos antes de la siguiente actualización
        time.sleep(300)
    
    except Exception as e:
        print(f"Error encontrado: {e}")
        time.sleep(300)  # Esperar 5 minutos antes de reintentar
