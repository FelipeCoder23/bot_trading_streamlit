def extraer_tendencias():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

    try:
        # Hacer la solicitud a la página de CoinMarketCap
        page = requests.get(url, headers=headers)
        page.raise_for_status()  # Verifica que la solicitud fue exitosa

        # Parsear el contenido HTML de la página
        soup = BeautifulSoup(page.content, 'html.parser')

        # 1. Extraer el precio actual de Bitcoin
        precio_tag = soup.find("span", {"data-test": "text-cdp-price-display"})
        if precio_tag:
            precio_actual = float(precio_tag.text.replace('$', '').replace(',', ''))
        else:
            precio_actual = None

        # 2. Extraer la tendencia
        tendencia_tag = soup.find("p", {"color": True, "data-change": True})
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

        # 3. Extraer la variación porcentual
        if tendencia_tag:
            # Extraer solo el valor del porcentaje
            variacion_text = tendencia_tag.text.split()[0]  # Tomar solo la primera parte (el número)
            variacion = float(variacion_text.replace('%', '').replace('\xa0', '').strip())
        else:
            variacion = None

        # Retornar el precio actual, variación y tendencia
        return precio_actual, variacion, tendencia

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return None, None, None
    


    # Llamar a la función para obtener el precio y la tendencia
precio_actual, variacion, tendencia = extraer_tendencias()

# Mostrar los resultados
print(f"Precio actual del Bitcoin: {precio_actual}")
print(f"Variación: {variacion}%")
print(f"Tendencia: {tendencia}")


#otro 
def extraer_tendencias():
    url = "https://coinmarketcap.com/currencies/bitcoin/"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

    try:
        # Hacer la solicitud a la página de CoinMarketCap
        page = requests.get(url, headers=headers)
        page.raise_for_status()  # Verifica que la solicitud fue exitosa

        # Parsear el contenido HTML de la página
        soup = BeautifulSoup(page.content, 'html.parser')

        # 1. Extraer el precio actual de Bitcoin
        precio_tag = soup.find("span", {"data-test": "text-cdp-price-display"})
        if precio_tag:
            precio_actual = float(precio_tag.text.replace('$', '').replace(',', ''))
        else:
            precio_actual = None

        # 2. Extraer la tendencia
        tendencia_tag = soup.find("p", {"color": True, "data-change": True})
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
        print(f"Error al realizar la solicitud: {e}")
        return None, None
    

precio, tendencia = extraer_tendencias()
print(f"Precio actual de Bitcoin: {precio}")
print(f"Tendencia: {tendencia}")


#limpioeza

# Función para limpiar y preparar los datos con gráficos de antes y después, y contar registros eliminados
def limpieza_datos_con_graficos(df_bitcoin):
    # Número inicial de datos
    num_datos_inicial = df_bitcoin.shape[0]

    # Copiar el DataFrame original para no modificarlo directamente
    df_bitcoin_limpio = df_bitcoin.copy()

    # Crear el gráfico de caja (boxplot) antes de la limpieza
    plt.figure(figsize=(10, 6))
    sns.boxplot(df_bitcoin_limpio['Close'])
    plt.title('Gráfico de caja - Antes de la limpieza')
    plt.xlabel('Precio de Cierre (Close)')
    plt.show()

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

    # Crear el gráfico de caja (boxplot) después de la limpieza
    plt.figure(figsize=(10, 6))
    sns.boxplot(df_bitcoin_limpio['Close'])
    plt.title('Gráfico de caja - Después de la limpieza')
    plt.xlabel('Precio de Cierre (Close)')
    plt.show()

    # Gráfico de dispersión para comparar el precio de cierre antes y después de la limpieza
    plt.figure(figsize=(14, 7))
    plt.plot(df_bitcoin.index, df_bitcoin['Close'], label='Antes de la limpieza', color='blue', alpha=0.5)
    plt.plot(df_bitcoin_limpio.index, df_bitcoin_limpio['Close'], label='Después de la limpieza', color='red', alpha=0.8)
    plt.title('Comparación del Precio de Cierre antes y después de la limpieza')
    plt.xlabel('Fecha')
    plt.ylabel('Precio de Cierre (Close)')
    plt.legend()
    plt.show()

    # Calcular el precio promedio de Bitcoin
    media_bitcoin = df_bitcoin_limpio['Close'].mean()

    # Número final de datos
    num_datos_final = df_bitcoin_limpio.shape[0]

    # Cantidad de datos eliminados
    datos_eliminados = num_datos_inicial - num_datos_final

    print(f"Número inicial de datos: {num_datos_inicial}")
    print(f"Número final de datos: {num_datos_final}")
    print(f"Datos eliminados durante la limpieza: {datos_eliminados}")

    return df_bitcoin_limpio, media_bitcoin