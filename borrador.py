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
