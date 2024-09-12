import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go

# Función para importar datos de Bitcoin
def importar_base_bitcoin():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Descargar datos de Bitcoin usando yfinance
    df_bitcoin = yf.download(tickers='BTC-USD', start=start_date.strftime('%Y-%m-%d'), 
                             end=end_date.strftime('%Y-%m-%d'), interval='5m')
    return df_bitcoin

# Función para extraer tendencias de CoinMarketCap
def extraer_tendencias():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    
    try:
        page = requests.get(url)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extraer el precio actual del Bitcoin
        precio_tag = soup.find("span", {"data-test": "text-cdp-price-display"})
        if precio_tag:
            precio_actual = float(precio_tag.text.replace('$', '').replace(',', ''))
        else:
            precio_actual = None
        
        # Extraer la variación de tendencia en porcentaje
        p_tags = soup.find_all("p")
        for p in p_tags:
            variacion_text = re.search(r"([-+]?\d*\.\d+|\d+)%", p.text)
            if variacion_text:
                variacion = float(variacion_text.group(0).replace('%', ''))
                tendencia = 'baja' if variacion < 0 else 'alta'
                return precio_actual, variacion, tendencia
    except requests.exceptions.RequestException:
        return None, None, None

# Función para limpiar datos
def limpieza_datos(df_bitcoin):
    df_bitcoin_limpio = df_bitcoin.copy()
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]
    
    # Rellenar valores nulos en 'Close'
    df_bitcoin_limpio['Close'] = df_bitcoin_limpio['Close'].ffill()
    
    # Eliminar registros con 'Volume' <= 0
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]
    
    # Calcular cuartiles y eliminar outliers
    Q1 = df_bitcoin_limpio['Close'].quantile(0.25)
    Q3 = df_bitcoin_limpio['Close'].quantile(0.75)
    IQR = Q3 - Q1
    df_bitcoin_limpio = df_bitcoin_limpio[(df_bitcoin_limpio['Close'] >= (Q1 - 1.5 * IQR)) & (df_bitcoin_limpio['Close'] <= (Q3 + 1.5 * IQR))]
    
    # Calcular media del precio
    media_bitcoin = df_bitcoin_limpio['Close'].mean()
    
    return df_bitcoin_limpio, media_bitcoin
# Función para calcular SMA
def calcular_sma(df_bitcoin, periodo_corto=10, periodo_largo=50):
    df_bitcoin['SMA_corto'] = df_bitcoin['Close'].rolling(window=periodo_corto).mean()
    df_bitcoin['SMA_largo'] = df_bitcoin['Close'].rolling(window=periodo_largo).mean()

    df_bitcoin['Signal'] = df_bitcoin.apply(lambda row: 1 if row['SMA_corto'] > row['SMA_largo'] else -1, axis=1)
    return df_bitcoin

# Función para tomar decisiones con SMA
def tomar_decisiones_con_sma(df_bitcoin):
    df_bitcoin['Decision'] = df_bitcoin.apply(lambda row: 'Comprar' if row['SMA_corto'] > row['SMA_largo'] 
                                              else 'Vender', axis=1)
    return df_bitcoin

# Visualización interactiva mejorada
def visualizacion_interactiva(df_bitcoin, media_bitcoin):
    df_bitcoin['Promedio'] = media_bitcoin
    
    # Crear una figura para el gráfico
    fig = go.Figure()
    
    # Agregar línea del precio de cierre
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['Close'], mode='lines', name='Precio de Cierre', line=dict(color='blue')))
    
    # Agregar línea del SMA corto y largo
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['SMA_corto'], mode='lines', name='SMA Corto', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_bitcoin.index, y=df_bitcoin['SMA_largo'], mode='lines', name='SMA Largo', line=dict(color='red', dash='dash')))
    
    # Configurar el título y las etiquetas
    fig.update_layout(title='Evolución del Precio del Bitcoin con SMA',
                      xaxis_title='Fecha',
                      yaxis_title='Precio en USD',
                      xaxis_rangeslider_visible=True)

    # Mostrar el gráfico
    return fig