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

# Función para extraer el precio actual y la tendencia desde CoinMarketCap
def extraer_tendencias():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    
    try:
        page = requests.get(url)
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extraer el precio actual del Bitcoin
        precio_tag = soup.find("div", class_="priceValue")
        if precio_tag:
            precio_text = precio_tag.text.strip()
            precio_actual = float(precio_text.replace('$', '').replace(',', '').replace('€', ''))
        else:
            precio_actual = None
        
        # Buscar el elemento <p> que contiene la variación porcentual
        variacion_tag = soup.find("p", attrs={"data-sensors-click": "true", "data-change": True})
        if variacion_tag:
            variacion_text = variacion_tag.get_text(strip=True)
            # Extraer el valor numérico usando expresiones regulares
            match = re.search(r"([-+]?\d*\.?\d+)%", variacion_text)
            if match:
                variacion = float(match.group(1))
                # Determinar la tendencia basándose en el atributo 'color'
                color = variacion_tag.get('color')
                if color == 'red':
                    tendencia = 'baja'
                    variacion = -abs(variacion)  # Asegurar que la variación sea negativa
                elif color == 'green':
                    tendencia = 'alta'
                    variacion = abs(variacion)  # Asegurar que la variación sea positiva
                else:
                    # Si no se puede determinar por el color, usamos 'data-change'
                    data_change = variacion_tag.get('data-change')
                    if data_change == 'down':
                        tendencia = 'baja'
                        variacion = -abs(variacion)
                    elif data_change == 'up':
                        tendencia = 'alta'
                        variacion = abs(variacion)
                    else:
                        tendencia = 'alta'  # Asumir 'alta' si no se puede determinar
                return precio_actual, variacion, tendencia
            else:
                return precio_actual, None, None
        else:
            return precio_actual, None, None
    except requests.exceptions.RequestException:
        return None, None, None

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

# Función para tomar decisiones basadas únicamente en las SMA
def tomar_decisiones_con_solo_sma(df_bitcoin):
    # Crear una columna 'Decision' inicializada con 'Mantener'
    df_bitcoin['Decision'] = 'Mantener'
    
    # Obtener las últimas SMA calculadas
    sma_corto_actual = df_bitcoin['SMA_corto'].iloc[-1]
    sma_largo_actual = df_bitcoin['SMA_largo'].iloc[-1]
    
    # Tomar decisión basada en SMA
    if sma_corto_actual > sma_largo_actual:
        decision = 'Comprar'
    elif sma_corto_actual < sma_largo_actual:
        decision = 'Vender'
    else:
        decision = 'Mantener'
    
    # Asignar la decisión al último registro usando .loc
    df_bitcoin.loc[df_bitcoin.index[-1], 'Decision'] = decision
    
    return df_bitcoin, decision


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
    jupyter
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








