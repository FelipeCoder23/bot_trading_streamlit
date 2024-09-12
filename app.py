import streamlit as st
import call_bitcoin  # Importar el archivo con las funciones

# Título de la aplicación
st.title('Bitcoin Trading Bot - SMA Implementation')

# Parámetros ajustables en la barra lateral
periodo_corto = st.sidebar.slider('Período de SMA corto', min_value=5, max_value=50, value=10)
periodo_largo = st.sidebar.slider('Período de SMA largo', min_value=20, max_value=100, value=50)

# 1. Obtener los datos de Bitcoin
df_bitcoin = call_bitcoin.importar_base_bitcoin()
st.write("Datos de Bitcoin cargados:")
st.write(df_bitcoin.head())

# 2. Extraer el precio actual y la tendencia
precio_actual, variacion, tendencia = call_bitcoin.extraer_tendencias()
if precio_actual:
    st.metric(label="Precio actual del Bitcoin", value=f"${precio_actual:,.2f}", delta=f"{variacion:.2f}%")
    st.write(f"Tendencia actual: {tendencia}")
else:
    st.write("Error al extraer las tendencias.")

# 3. Limpiar los datos de Bitcoin
df_bitcoin, media_bitcoin = call_bitcoin.limpieza_datos(df_bitcoin)
st.write(f"Precio promedio de Bitcoin después de la limpieza: {media_bitcoin:.2f} USD")

# 4. Calcular SMA y generar señales
df_bitcoin = call_bitcoin.calcular_sma(df_bitcoin, periodo_corto, periodo_largo)
st.write("Señales de compra/venta basadas en SMA:")
st.write(df_bitcoin[['SMA_corto', 'SMA_largo', 'Signal']].tail())

# 5. Tomar decisiones de compra/venta
df_bitcoin = call_bitcoin.tomar_decisiones_con_sma(df_bitcoin)
st.write("Decisiones basadas en SMA:")
st.write(df_bitcoin[['SMA_corto', 'SMA_largo', 'Decision']].tail())

# 6. Visualizar el gráfico interactivo
fig = call_bitcoin.visualizacion_interactiva(df_bitcoin, media_bitcoin)
st.plotly_chart(fig)
