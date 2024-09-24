import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
import plotly.graph_objects as go

# Función para obtener datos históricos de Bitcoin
def importar_base_bitcoin():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Descargar datos de Bitcoin usando yfinance
    df_bitcoin = yf.download(
        tickers='BTC-USD',
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        interval='5m'
    )
    return df_bitcoin

# Función para extraer el precio y la tendencia desde CoinMarketCap
def extraer_tendencias():
    global df_bitcoin, df_bitcoin_limpio, precio_actual, tendencia, media_bitcoin, algoritmo_decision, color

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
    url = 'https://coinmarketcap.com/currencies/bitcoin/'

    try:
        # Realizar la solicitud con los headers para evitar ser bloqueado
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status()
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
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud: {e}")
        return None, None

# Función para limpiar y preparar los datos
def limpieza_datos(df_bitcoin):
    # Copiar el DataFrame original para no modificarlo directamente
    df_bitcoin_limpio = df_bitcoin.copy()
    
    # Eliminar índices duplicados
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]
    
    # Rellenar valores nulos en la columna 'Close' con el último valor válido
    df_bitcoin_limpio['Close'] = df_bitcoin_limpio['Close'].ffill()
    
    # Eliminar filas donde el volumen sea menor o igual a cero
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]
    
    # Calcular los cuartiles para identificar y eliminar valores atípicos
    Q1 = df_bitcoin_limpio['Close'].quantile(0.25)
    Q3 = df_bitcoin_limpio['Close'].quantile(0.75)
    IQR = Q3 - Q1
    df_bitcoin_limpio = df_bitcoin_limpio[
        (df_bitcoin_limpio['Close'] >= (Q1 - 1.5 * IQR)) &
        (df_bitcoin_limpio['Close'] <= (Q3 + 1.5 * IQR))
    ]
    
    # Calcular el precio promedio de Bitcoin
    media_bitcoin = df_bitcoin_limpio['Close'].mean()
    
    return df_bitcoin_limpio, media_bitcoin

# Función para calcular las medias móviles simples (SMA)
def calcular_sma(df_bitcoin, periodo_corto=10, periodo_largo=50):
    # Calcular la SMA de corto y largo plazo
    df_bitcoin['SMA_corto'] = df_bitcoin['Close'].rolling(window=periodo_corto).mean()
    df_bitcoin['SMA_largo'] = df_bitcoin['Close'].rolling(window=periodo_largo).mean()
    
    return df_bitcoin

# Función para tomar decisiones basadas en SMA y la tendencia
def tomar_decisiones(df_bitcoin, precio_actual, tendencia, media_bitcoin):
    # Obtener las últimas SMA calculadas
    sma_corto_actual = df_bitcoin['SMA_corto'].iloc[-1]
    sma_largo_actual = df_bitcoin['SMA_largo'].iloc[-1]

    # Algoritmo de decisión basado en SMA y tendencia actuales
    if (sma_corto_actual > sma_largo_actual) and (tendencia == 'alta'):
        decision = 'Comprar'
        color = '#228b22'  # Verde, señal de compra
        print(f"Decisión: {decision} - SMA corta > SMA larga y tendencia alcista.")

    elif (sma_corto_actual < sma_largo_actual) and (tendencia == 'baja'):
        decision = 'Vender'
        color = '#dc143c'  # Rojo, señal de venta
        print(f"Decisión: {decision} - SMA corta < SMA larga y tendencia bajista.")

    else:
        decision = 'Mantener'
        color = '#000000'  # Negro, señal de mantener
        print(f"Decisión: {decision} - No hay una señal clara.")

    # Asignar la decisión al último registro usando .loc
    df_bitcoin.loc[df_bitcoin.index[-1], 'Decision'] = decision
    
    # Retornar el DataFrame modificado y la decisión tomada
    return df_bitcoin, decision, color


# Función para visualizar los datos
def visualizacion_interactiva(df_bitcoin, media_bitcoin):
    # Agregar una columna con el precio promedio
    df_bitcoin['Promedio'] = media_bitcoin
    
    # Crear una figura para el gráfico
    fig = go.Figure()
    
    # Agregar el precio de cierre
    fig.add_trace(go.Scatter(
        x=df_bitcoin.index,
        y=df_bitcoin['Close'],
        mode='lines',
        name='Precio de Cierre',
        line=dict(color='blue')
    ))
    
    # Agregar las medias móviles
    fig.add_trace(go.Scatter(
        x=df_bitcoin.index,
        y=df_bitcoin['SMA_corto'],
        mode='lines',
        name='SMA Corto',
        line=dict(color='green')
    ))
    fig.add_trace(go.Scatter(
        x=df_bitcoin.index,
        y=df_bitcoin['SMA_largo'],
        mode='lines',
        name='SMA Largo',
        line=dict(color='red', dash='dash')
    ))
    
    # Añadir puntos de compra/venta
    buy_signals = df_bitcoin[df_bitcoin['Decision'] == 'Comprar']
    sell_signals = df_bitcoin[df_bitcoin['Decision'] == 'Vender']
    
    fig.add_trace(go.Scatter(
        x=buy_signals.index,
        y=buy_signals['Close'],
        mode='markers',
        name='Comprar',
        marker=dict(color='green', symbol='triangle-up', size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=sell_signals.index,
        y=sell_signals['Close'],
        mode='markers',
        name='Vender',
        marker=dict(color='red', symbol='triangle-down', size=10)
    ))
    
    # Configurar el diseño del gráfico
    fig.update_layout(
        title='Evolución del Precio del Bitcoin con SMA y Señales de Compra/Venta',
        xaxis_title='Fecha',
        yaxis_title='Precio en USD',
        xaxis_rangeslider_visible=True
    )
    
    return fig








