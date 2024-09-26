# 📊 Bot de Trading de Bitcoin con Medias Móviles Simples (SMA)

## 📈 Objetivo del Proyecto
Este proyecto implementa un bot de trading para Bitcoin utilizando el análisis de medias móviles simples (SMA) y visualización de datos interactiva en Streamlit. El bot analiza los precios históricos de Bitcoin, calcula las medias móviles y toma decisiones de compra, venta o mantener en función de estos indicadores y de la tendencia del mercado.

## 🛠️ Funcionalidades
- **Importar datos históricos de Bitcoin**: Utiliza la API de `yfinance` para descargar precios históricos de Bitcoin con un intervalo de 5 minutos.
- **Extracción de tendencias**: Realiza scraping de la página de CoinMarketCap para obtener el precio actual de Bitcoin y su tendencia (alcista o bajista).
- **Limpieza de datos**: Elimina valores nulos y atípicos, y rellena datos faltantes.
- **Cálculo de SMA**: Calcula las medias móviles simples (SMA) de corto y largo plazo con parámetros ajustables.
- **Toma de decisiones**: Basado en las SMA y la tendencia, el bot sugiere si comprar, vender o mantener.
- **Visualización interactiva**: Muestra gráficos interactivos con los precios de cierre de Bitcoin, las medias móviles y las señales de compra/venta.
- **Actualización automática**: La aplicación se actualiza automáticamente cada 5 minutos.

## ⚙️ Instalación

### Requisitos
- **Python 3.7+** 
- **Bibliotecas**: Este proyecto utiliza las siguientes bibliotecas de Python, que se pueden instalar usando el archivo `requirements.txt`.

### Clonar el repositorio

```bash
git clone https://github.com/usuario/bitcoin-trading-bot.git
cd bitcoin-trading-bot
```

### 🔧 Instalar las dependencias

Puedes instalar todas las dependencias necesarias ejecutando el siguiente comando:

```bash
pip install -r requirements.txt
```

### 🚀 Ejecución del proyecto

Para ejecutar la aplicación en local, usa el siguiente comando:

```bash
streamlit run app.py
```
Esto abrirá una aplicación web interactiva en tu navegador en http://localhost:8501/.

### 📝 Uso
1. Ajusta los parámetros de SMA desde la barra lateral para modificar los periodos de corto y largo plazo.
2. El bot calculará automáticamente las SMA y mostrará las decisiones en tiempo real: Comprar, Vender o Mantener.
3. Visualiza los datos históricos, las SMA, y las señales de compra/venta en el gráfico interactivo.

### 📁 Archivos clave
- **`call_bitcoin.py`**: Contiene las funciones principales para obtener datos históricos de Bitcoin, extraer tendencias, limpiar los datos, calcular las SMA y tomar decisiones.
- **`app.py`**: Es el archivo principal que corre la aplicación de Streamlit, integrando las funciones del bot de trading y la visualización interactiva.


  
