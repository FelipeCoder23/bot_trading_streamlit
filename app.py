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
if precio_actual is not None and variacion is not None:
    st.metric(
        label="Precio actual del Bitcoin",
        value=f"${precio_actual:,.2f}",
        delta=f"{variacion:.2f}%"
    )
    st.write(f"Tendencia actual: **{tendencia.capitalize()}**")
else:
    st.write("No se pudo obtener la tendencia actual.")

# 3. Limpiar los datos de Bitcoin
st.write("Limpiando datos...")
df_bitcoin, media_bitcoin = call_bitcoin.limpieza_datos(df_bitcoin)
st.write(f"Precio promedio después de la limpieza: **${media_bitcoin:.2f}**")

# 4. Calcular SMA
st.write("Calculando Medias Móviles Simples (SMA)...")
df_bitcoin = call_bitcoin.calcular_sma(df_bitcoin, periodo_corto, periodo_largo)
st.write("SMA calculadas:")
st.dataframe(df_bitcoin[['Close', 'SMA_corto', 'SMA_largo']].tail())

# 5. Tomar decisiones integrando SMA y tendencia
st.write("Determinando decisiones de compra/venta...")
df_bitcoin, decision_final = call_bitcoin.tomar_decisiones_con_sma_y_tendencia(df_bitcoin, precio_actual, tendencia)
st.write("Decisiones basadas en SMA y tendencia:")
st.dataframe(df_bitcoin[['Close', 'SMA_corto', 'SMA_largo', 'Decision']].tail())

# 6. Mostrar la decisión final con fundamentación
sma_corto_actual = df_bitcoin['SMA_corto'].iloc[-1]
sma_largo_actual = df_bitcoin['SMA_largo'].iloc[-1]

if decision_final == 'Comprar':
    st.subheader(f"Según estos datos, se toma la decisión de **comprar**.")
    st.write(f"Esto se debe a que la SMA de corto plazo ({sma_corto_actual:.2f}) es mayor que la SMA de largo plazo ({sma_largo_actual:.2f}) y la tendencia actual es **{tendencia}**.")
elif decision_final == 'Vender':
    st.subheader(f"Según estos datos, se toma la decisión de **vender**.")
    st.write(f"Esto se debe a que la SMA de corto plazo ({sma_corto_actual:.2f}) es menor que la SMA de largo plazo ({sma_largo_actual:.2f}) y la tendencia actual es **{tendencia}**.")
else:
    st.subheader(f"Según estos datos, se recomienda **mantener** la posición.")
    st.write(f"La SMA de corto plazo ({sma_corto_actual:.2f}) y la SMA de largo plazo ({sma_largo_actual:.2f}) no muestran una señal clara, o la tendencia actual es **{tendencia}**.")

# 7. Visualizar el gráfico interactivo
st.write("Visualizando datos...")
fig = call_bitcoin.visualizacion_interactiva(df_bitcoin, media_bitcoin)
st.plotly_chart(fig)
