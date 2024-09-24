import streamlit as st
import call_bitcoin  # Importar el archivo con las funciones

# Configurar la página
st.set_page_config(page_title='Bot de Trading de Bitcoin', layout='wide', initial_sidebar_state="expanded")

# Colocar el logo y el título en la misma línea con HTML y CSS
st.markdown("""
    <div style="display: inline-flex; align-items: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/46/Bitcoin.svg" alt="Bitcoin Logo" width="50">
        <h1 style='color: #f63366; margin-left: 10px;'>Bot de Trading de Bitcoin - Implementación de SMA</h1>
    </div>
""", unsafe_allow_html=True)

# Parámetros ajustables en la barra lateral
st.sidebar.header('Parámetros de SMA')
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/46/Bitcoin.svg", width=80)
periodo_corto = st.sidebar.slider(
    'Período de SMA corto',
    min_value=5,
    max_value=50,
    value=10,
    step=1
)
periodo_largo = st.sidebar.slider(
    'Período de SMA largo',
    min_value=20,
    max_value=100,
    value=50,
    step=1
)

# PROCESAMIENTO DETRÁS DE ESCENA
df_bitcoin = call_bitcoin.importar_base_bitcoin()
precio_actual, tendencia = call_bitcoin.extraer_tendencias()
df_bitcoin_limpio, media_bitcoin = call_bitcoin.limpieza_datos(df_bitcoin)
df_bitcoin_limpio = call_bitcoin.calcular_sma(df_bitcoin_limpio, periodo_corto, periodo_largo)
df_bitcoin_limpio, decision_final, color = call_bitcoin.tomar_decisiones(df_bitcoin_limpio, precio_actual, tendencia, media_bitcoin)

# Obtener las últimas SMA calculadas
sma_corto_actual = df_bitcoin_limpio['SMA_corto'].iloc[-1]
sma_largo_actual = df_bitcoin_limpio['SMA_largo'].iloc[-1]

# MOSTRAR RESULTADOS EN LA INTERFAZ
col1, col2 = st.columns(2)

with col1:
    st.metric("Precio actual del Bitcoin", f"${precio_actual:,.2f}")
    st.write(f"Tendencia actual: **{tendencia.capitalize()}**")

with col2:
    st.subheader("Parámetros de SMA:")
    st.write(f"- Período corto: {periodo_corto}")
    st.write(f"- Período largo: {periodo_largo}")

# Mostrar íconos según la decisión final
icon_comprar = "https://cdn-icons-png.flaticon.com/512/2698/2698194.png"
icon_vender = "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
if decision_final == 'Comprar':
    st.image(icon_comprar, width=50)
    st.success(f"Decisión final: **Comprar** - La SMA de corto plazo ({sma_corto_actual:.2f}) ha cruzado por encima de la SMA de largo plazo ({sma_largo_actual:.2f}) y {tendencia}.")
elif decision_final == 'Vender':
    st.image(icon_vender, width=50)
    st.error(f"Decisión final: **Vender** - La SMA de corto plazo ({sma_corto_actual:.2f}) ha cruzado por debajo de la SMA de largo plazo ({sma_largo_actual:.2f}) y {tendencia}.")
else:
    st.warning(f"Decisión final: **Mantener** - La SMA de corto plazo ({sma_corto_actual:.2f}) y la SMA de largo plazo ({sma_largo_actual:.2f}) no muestran una señal clara y {tendencia}.")

# Expander para detalles técnicos adicionales
with st.expander("Ver detalles técnicos"):
    st.write("Aquí puedes ver los datos crudos y resultados intermedios.")
    st.dataframe(df_bitcoin_limpio)

# Gráfico y pie de página
st.write("Visualizando datos...")
fig = call_bitcoin.visualizacion_interactiva(df_bitcoin_limpio, media_bitcoin)
st.plotly_chart(fig)

# Pie de página
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Datos obtenidos de <a href='https://coinmarketcap.com/'>CoinMarketCap</a></p>", unsafe_allow_html=True)
