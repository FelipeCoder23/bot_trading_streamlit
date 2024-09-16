import streamlit as st
import call_bitcoin  # Importar el archivo con las funciones

# Configurar la página
st.set_page_config(page_title='Bot de Trading de Bitcoin', layout='wide')

# Título de la aplicación
st.title('Bot de Trading de Bitcoin - Implementación de SMA')

# Parámetros ajustables en la barra lateral
st.sidebar.header('Parámetros de SMA')
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

# 1. Obtener los datos de Bitcoin
st.write("Obteniendo datos de Bitcoin...")
df_bitcoin = call_bitcoin.importar_base_bitcoin()
st.write("Datos de Bitcoin:")
st.dataframe(df_bitcoin.tail())

# 2. Extraer el precio actual y la tendencia
st.write("Extrayendo tendencias actuales...")
precio_actual, variacion, tendencia = call_bitcoin.extraer_tendencias()
if precio_actual is not None and variacion is not None and tendencia is not None:
    st.metric(
        label="Precio actual del Bitcoin",
        value=f"${precio_actual:,.2f}",
        delta=f"{variacion:.2f}%",
        delta_color="inverse"  # Ajusta el color según sea positivo o negativo
    )
    st.write(f"Tendencia actual: **{tendencia.capitalize()}**")
else:
    st.write("No se pudo obtener la tendencia actual. Verifica tu conexión o intenta más tarde.")


# 3. Limpiar los datos de Bitcoin
st.write("Limpiando datos...")
df_bitcoin_limpio, media_bitcoin = call_bitcoin.limpieza_datos(df_bitcoin)
st.write(f"Precio promedio después de la limpieza: **${media_bitcoin:.2f}**")

# 4. Calcular SMA usando el DataFrame limpio
st.write("Calculando Medias Móviles Simples (SMA)...")
df_bitcoin_limpio = call_bitcoin.calcular_sma(df_bitcoin_limpio, periodo_corto, periodo_largo)
st.write("SMA calculadas:")
st.dataframe(df_bitcoin_limpio[['Close', 'SMA_corto', 'SMA_largo']].tail())

# 5. Tomar decisiones basadas únicamente en las SMA
st.write("Determinando decisiones de compra/venta basadas en SMA...")

# Llamar a la función que solo usa SMA
df_bitcoin_limpio, decision_final = call_bitcoin.tomar_decisiones_con_solo_sma(df_bitcoin_limpio)
st.write("Decisiones basadas en SMA:")
st.dataframe(df_bitcoin_limpio[['Close', 'SMA_corto', 'SMA_largo', 'Decision']].tail())

# Mostrar la decisión final basada en SMA
sma_corto_actual = df_bitcoin_limpio['SMA_corto'].iloc[-1]
sma_largo_actual = df_bitcoin_limpio['SMA_largo'].iloc[-1]

if decision_final == 'Comprar':
    st.subheader(f"Según estos datos, se toma la decisión de **comprar**.")
    st.write(f"Esto se debe a que la SMA de corto plazo ({sma_corto_actual:.2f}) ha cruzado por encima de la SMA de largo plazo ({sma_largo_actual:.2f}).")
elif decision_final == 'Vender':
    st.subheader(f"Según estos datos, se toma la decisión de **vender**.")
    st.write(f"Esto se debe a que la SMA de corto plazo ({sma_corto_actual:.2f}) ha cruzado por debajo de la SMA de largo plazo ({sma_largo_actual:.2f}).")
else:
    st.subheader(f"Según estos datos, se recomienda **mantener** la posición.")
    st.write(f"La SMA de corto plazo ({sma_corto_actual:.2f}) y la SMA de largo plazo ({sma_largo_actual:.2f}) no muestran una señal clara.")
# 7. Visualizar el gráfico interactivo usando el DataFrame limpio
st.write("Visualizando datos...")
fig = call_bitcoin.visualizacion_interactiva(df_bitcoin_limpio, media_bitcoin)
st.plotly_chart(fig)
