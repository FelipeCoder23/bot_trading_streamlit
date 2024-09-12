import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
import re  # Importar la librería de expresiones regulares

import matplotlib.pyplot as plt


from IPython.display import clear_output
import time

# Variables globales
global df_bitcoin, precio_actual, tendencia, media_bitcoin, algoritmo_decision


# Definimos la función importar_base_bitcoin
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



def extraer_tendencias():
    global precio_actual, tendencia
    
    # URL de la página que vamos a hacer scraping
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    
    try:
        # Realizamos una solicitud a la página web
        page = requests.get(url)
        page.raise_for_status()  # Verifica que la solicitud fue exitosa
        
        # Creamos el objeto BeautifulSoup para analizar la página
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Extraemos el precio actual del Bitcoin usando la nueva clase y atributo 'data-test'
        precio_tag = soup.find("span", {"data-test": "text-cdp-price-display"})
        if precio_tag:
            precio_actual = float(precio_tag.text.replace('$', '').replace(',', ''))
            print(f"Precio actual del Bitcoin: ${precio_actual}")
        else:
            print("No se pudo extraer el precio actual del Bitcoin.")
        
        # Filtrar los párrafos que contienen la variación en porcentaje
        p_tags = soup.find_all("p")
        for p in p_tags:
            # Usar una expresión regular para buscar números con el símbolo '%'
            variacion_text = re.search(r"([-+]?\d*\.\d+|\d+)%", p.text)
            if variacion_text:
                # Extraer el valor de la variación
                variacion = float(variacion_text.group(0).replace('%', ''))  # Convertimos a float sin el símbolo %
                
                # Definir la tendencia según el valor extraído
                if variacion < 0:
                    tendencia = 'baja'
                else:
                    tendencia = 'alta'
                
                print(f"Variación: {variacion}% - Tendencia: {tendencia}")
                break  # Salimos después de encontrar la primera variación válida
        
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la página: {e}")



# Llamar a la función para limpiar datos


def limpieza_datos():
    global df_bitcoin, media_bitcoin
    
    # Crear una copia de df_bitcoin para realizar la limpieza
    df_bitcoin_limpio = df_bitcoin.copy()
    
    # Verificar duplicados en el índice Datetime
    df_bitcoin_limpio = df_bitcoin_limpio[~df_bitcoin_limpio.index.duplicated(keep='first')]

    # Tratar valores nulos en la columna 'Close' usando ffill() sin inplace
    df_bitcoin_limpio['Close'] = df_bitcoin_limpio['Close'].ffill()  # Llenar con el último valor válido

    # Eliminar registros con 'Volume' <= 0
    df_bitcoin_limpio = df_bitcoin_limpio[df_bitcoin_limpio['Volume'] > 0]
    
    # Identificación de outliers utilizando un gráfico de boxplot para la columna 'Close'
    plt.figure(figsize=(10, 5))
    plt.boxplot(df_bitcoin_limpio['Close'])
    plt.title('Detección de outliers en la columna Close')
    plt.show()

    # Cálculo de cuartiles
    Q1 = df_bitcoin_limpio['Close'].quantile(0.25)
    Q3 = df_bitcoin_limpio['Close'].quantile(0.75)
    IQR = Q3 - Q1

    # Filtrar registros cuyos precios (Close) estén entre el 1er cuartil y el 3er cuartil
    df_bitcoin_limpio = df_bitcoin_limpio[(df_bitcoin_limpio['Close'] >= Q1) & (df_bitcoin_limpio['Close'] <= Q3)]
    
    # Calcular el precio promedio de 'Close' después de la limpieza
    media_bitcoin = df_bitcoin_limpio['Close'].mean()
    
    # Mostrar información final
    print(f"Precio promedio de Bitcoin después de la limpieza: {media_bitcoin:.2f} USD")
    print(f"Registros finales después de la limpieza: {df_bitcoin_limpio.shape[0]} registros")

# Ejecutar la función



def tomar_decisiones():
    global precio_actual, media_bitcoin, tendencia, algoritmo_decision

    # Criterio de decisión
    if precio_actual >= media_bitcoin and tendencia == 'baja':
        algoritmo_decision = 'Vender'
    elif precio_actual < media_bitcoin and tendencia == 'alta':
        algoritmo_decision = 'Comprar'
    else:
        algoritmo_decision = ''

    # Imprimir la decisión tomada
    print(f"Decisión: {algoritmo_decision}")



# Llamar a la función para lvisualizar 

def visualizacion():
    global df_bitcoin, media_bitcoin, algoritmo_decision
    
    # Agregar la columna 'Promedio' al dataframe df_bitcoin con el valor de media_bitcoin
    df_bitcoin['Promedio'] = media_bitcoin
    
    # Configurar el tamaño del gráfico
    plt.figure(figsize=(16, 5))
    
    # Agregar título al gráfico
    plt.title('Evolución del precio del Bitcoin y decisión del algoritmo')

    # Dibujar la línea del precio de cierre ('Close')
    plt.plot(df_bitcoin.index, df_bitcoin['Close'], label='Precio de cierre', color='blue')

    # Dibujar la línea del promedio ('Promedio')
    plt.plot(df_bitcoin.index, df_bitcoin['Promedio'], label='Promedio', color='red', linestyle='--')

    # Mostrar la decisión en el gráfico con el método annotate()
    decision_text = f"Decisión: {algoritmo_decision}"
    plt.annotate(decision_text, xy=(df_bitcoin.index[-1], df_bitcoin['Close'].iloc[-1]),
                 xytext=(df_bitcoin.index[-30], df_bitcoin['Close'].max()),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=12, color='green')

    # Añadir leyenda
    plt.legend()

    # Mostrar el gráfico
    plt.show()





# Limpiar la pantalla para evitar la acumulación de gráficos anteriores
clear_output(wait=True)

# Ejecutar las funciones en el orden correcto
importar_base_bitcoin()    # Obtener los datos históricos del Bitcoin
extraer_tendencias()       # Extraer la tendencia del sitio web
limpieza_datos()           # Limpiar y procesar los datos
tomar_decisiones()         # Tomar la decisión basada en las reglas del algoritmo
visualizacion()            # Mostrar el gráfico actualizado